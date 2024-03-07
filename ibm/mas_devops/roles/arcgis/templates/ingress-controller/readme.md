## Ingress-controller setup

The `ingress-controller.yaml` file in this folder is a combination of the two official yaml files:

1.) Manditory

    https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/mandatory.yaml

2.) Service Nodeport

    https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/baremetal/service-nodeport.yaml


A modification was made to allow for larger file downloads.  The default is 1MB.  This limit was raised to 10MB with this line in ingress-controller.yaml:
```yaml
...
kind: ConfigMap
apiVersion: v1
metadata:
  name: nginx-configuration
  namespace: ingress-nginx
data:
  proxy-body-size: ${PROXY_BODY_SIZE}   <-- modification
...
```
Update the ingress-controller.properties file to increase/decrease this value.

Then run the ./deploy.sh to deploy the ingress controller to your cluster.

This will create the namespace `ingress-nginx` and four pods:
```
kubectl get all -n ingress-nginx
NAME                                           READY   STATUS    RESTARTS   AGE
pod/nginx-ingress-controller-dfc844959-hvjxs   1/1     Running   0          10m

NAME                    TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
service/ingress-nginx   NodePort   10.105.92.73   <none>        80:31040/TCP,443:32647/TCP   9m43s

NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx-ingress-controller   1/1     1            1           10m

NAME                                                 DESIRED   CURRENT   READY   AGE
replicaset.apps/nginx-ingress-controller-dfc844959   1         1         1       10m
```

Once this is done you should be able to reach your cluster from outside (e.g. a reverse proxy).

NOTE: If you recreate your ingress-controller a new NodePort will be assigned.  If you're using a reverse proxy you will need to change the nginx _default_ config file:

For example the ingress-inginx service below is using https port 32647:
```console
kubectl get service ingress-nginx -n ingress-nginx                                                                                                                                         1 ↵
NAME            TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx   NodePort   10.105.92.73   <none>        80:31040/TCP,443:32647/TCP   50m
```

So you would also need to change your reverse proxy's nginx config file /etc/nginx/sites-available/default to use https port 32647:
```
    . . .
    location /k8s/dashboard/ {
        proxy_pass https://dev0008611.esri.com:32647/;
    }

    location /gis/ {
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Request-Context $scheme://$host/gis/;
        proxy_read_timeout 600s;
        proxy_pass https://dev0008611.esri.com:32647/gis/;
    }

```
