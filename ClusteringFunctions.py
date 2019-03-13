'''
def agrupaClusters():
    todosClustersLocal = todosClusters
    erro = 0
    while(erro == 0):
        todosClustersSorted = sorted(todosClustersLocal, key=Cluster.getQuantEsquinas)
        menorDist = 20000
        centroidPrin = todosClustersSorted[0].getCentroid()
        cont = 0
        posMenorDist = 0
        erro = 1
        for i in todosClustersSorted:
            if cont != 0:
                centClusters = i.getCentroid()
                distan = distancia(centClusters[0], centClusters[1], centroidPrin[0], centroidPrin[1])
                if ((len(i.getEsquinas()) + len(todosClustersSorted[0].getEsquinas())) < esqMax) and (distan < menorDist)\
                        and((distancia(centClusters[0], centClusters[1], cOfficeLat, cOfficeLon) + distan) < distanciaTeste):
                    erro = 0
                    menorDist = distan
                    posMenorDist = cont
            cont = cont + 1

        if(erro == 0):
            for x in todosClustersSorted[0].getEsquinas():
                todosClustersSorted[posMenorDist].setEsquinas(x)

            del(todosClustersSorted[0])
            todosClustersLocal = todosClustersSorted

    return todosClustersLocal


def kMeans(npLat, npLon, esqMin):
    X = np.array(list(zip(npLat, npLon)))
    # Number of clusters
    k = 2
    C_x = []
    C_y = []
    # X coordinates of random centroids
    for i in range(k):
        randomNodeId = random.choice(listaIdPtos)
        randomNode = pontos[randomNodeId]
        C_x.append(randomNode.getLat())
        C_y.append(randomNode.getLon())

    C = np.array(list(zip(C_x, C_y)), dtype=np.float32)

    # To store the value of centroids when it updates
    C_old = np.zeros(C.shape)
    for i in range(len(C_old)):
        C_old[i][0] = np.amin(npLat)
        C_old[i][1] = np.amin(npLon)

    # Cluster Lables(0, 1, 2)
    clusters = np.zeros(len(X))

    # Error func. - Distance between new centroids and old centroids
    latC, lonC = zip(*C)
    latOld, lonOld = zip(*C_old)
    erros = []
    for i in range(len(C)):
        erros.append(distancia(latC[i], lonC[i], latOld[i], lonOld[i]))
    error = np.linalg.norm(erros)
    # Loop will run till the error becomes zero

    latX, lonX = zip(*X)
    while error != 0:
        # Assigning each value to its closest cluster
        for i in range(len(X)):
            distances = []
            for j in range(len(C)):
                distances.append(np.linalg.norm(distancia(latX[i], lonX[i], latC[j], lonC[j])))

            cluster = np.argmin(distances)
            clusters[i] = cluster
        # Storing the old centroid values
        C_old = deepcopy(C)
        # Finding the new centroids by taking the average value
        for i in range(k):
            points = [X[j] for j in range(len(X)) if clusters[j] == i]
            if len(points) > 0:
                C[i] = np.mean(points, axis=0)

        latOld, lonOld = zip(*C_old)
        erros = []
        for x in range(len(C)):
            erros.append(distancia(latC[x], lonC[x], latOld[x], lonOld[x]))
        error = np.linalg.norm(erros)

   #fig, ax = plt.subplots()
    pointsAux = []
    distMax = 250
    latCaux, lonCaux = zip(*C)
    for i in range(k):
        points = np.array([X[j] for j in range(len(X)) if clusters[j] == i])
        distCent = [distancia(p[0], p[1], latCaux[i], lonCaux[i]) for p in points]
        if len(points) == 0:
            continue
        infracoes = len([1 for d in distCent if (d > distMax)])
        if (len(points) < esqMin) and infracoes == 0:
            pointsAux.append(points)
            cor = random.choice(colors).get_hex_l()
            ax.scatter(latCaux[i], lonCaux[i], marker='x', s=10, c='#000033')

            clusterAux = Cluster()
            clusterAux.setCentroid(latCaux[i], lonCaux[i])
            for k in points:
                clusterAux.setEsquinas(k)

            todosClusters.append(clusterAux)
            for desenhaLinha in points:
                #print(desenhaLinha[0])
                ax.add_line(mlines.Line2D([latCaux[i], desenhaLinha[0]], [lonCaux[i], desenhaLinha[1]], c = cor))
                #plt.plot(latCaux[i], lonCaux[i], desenhaLinha[0], desenhaLinha[1], marker='o', c = cor)
        else:
            pointsAuxRec = kMeans(points[:, 0], points[:, 1], esqMin)
            for j in pointsAuxRec:
                pointsAux.append(j)

    return  pointsAux'''