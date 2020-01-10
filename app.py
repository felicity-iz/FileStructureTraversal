from flask import Flask
from flask import request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route("/")
def psych():
    return "lets get crackin"

@app.route("/getFileStructure", methods = ['POST'])
def getFileStructure():
    if not request.is_json:
        return "Sorry, no Json Request"
    content = request.get_json()
    data = json.dumps(content)
    hierarchy = json.loads(data)

    graph = []

    for folder in hierarchy:
        if(folder['parent'])== 1:
            relation = str(folder['parent'])+"(root)" + " --> " + str(folder['id']) + "(" + str(folder['name']) + ")"
            graph.append(relation)
        else:
            relation = str(folder['parent']) + " --> " + str(folder['id'])+"("+str(folder['name'])+")"
            graph.append(relation)

    seperator = "\n"
    graphLinks = seperator.join(graph)
    graphLinks = "graph TD\n" + graphLinks
    print(graphLinks)

    return graphLinks


@app.route('/getHierarchy/<parentId>', methods = ['POST'])
def getChildren(parentId):

    parentId = int(parentId)
    if not request.is_json:
        return "Sorry, no Json Request"

    content = request.get_json()
    data = json.dumps(content)
    list = json.loads(data)

    #ASSUMPTION: this is a top down tree hierarchy where each node can only have one parent

    children = []
    unresolved = []
    unresolvedObjects = []
    childrenObjects = []
    removed = []

    def assignIDs(relation):
        for previous in unresolved:
            relation.append(previous)
        unresolved.clear()

    def assignObjects(action):
        if(action == "remove"):
            for element in unresolvedObjects:
                list.remove(element)
            unresolvedObjects.clear()
        if(action == "append"):
            for element in unresolvedObjects:
                childrenObjects.append(element)
                list.remove(element)
            unresolvedObjects.clear()

    def checkNode(folder):
        print("\n")
        print("check node"+ str(folder['id']))
        #print("children")
        #print(' '.join(str(id) for id in children))
        #print("removed:")
        #print(' '.join(str(id) for id in removed))
        #print("unresolved:")
        #print(' '.join(str(id) for id in unresolved))
        if folder['parent'] == 1:
            print("got to root without finding parent")
            removed.append(folder['id'])
            list.remove(folder)
            if len(unresolvedObjects) != 0:
                assignObjects("remove")
                assignIDs(removed)
            traverseNodes()
            return
        if folder['id'] == parentId:
            print(str(folder['id']) + "is self")
            removed.append(folder['id'])
            list.remove(folder)
            traverseNodes()
            return
        if folder['parent'] == parentId:
            print(" direct child")
            children.append(folder['id'])
            childrenObjects.append(folder)
            list.remove(folder)
            if len(unresolvedObjects) != 0:
                assignObjects("append")
                assignIDs(children)
            traverseNodes()
            return
        if folder['parent'] in removed:
            print(" child of removed ")
            removed.append(folder['id'])
            list.remove(folder)
            if len(unresolvedObjects) != 0:
                assignObjects("remove")
                assignIDs(removed)
            traverseNodes()
            return
        if folder['parent'] in children:
            print(" child of child ")
            children.append(folder['id'])
            childrenObjects.append(folder)
            list.remove(folder)
            if len(unresolvedObjects) != 0:
                assignObjects("append")
                assignIDs(children)
            traverseNodes()
            return
        #print(str(folder['id']) + " is unresolved")
        unresolved.append(folder['id'])
        unresolvedObjects.append(folder)
        currentParent = folder['parent']
        #find parent
        for elem in list:
            if (elem['id'] == currentParent):
                checkNode(elem)

    def traverseNodes():
        for folder in list:
            checkNode(folder)


    if parentId == 1:
        return data;
    else:
        traverseNodes()

    childrenJson = json.dumps(childrenObjects)
    return childrenJson

if __name__ == "__main__":
    app.run()(debug=True)
