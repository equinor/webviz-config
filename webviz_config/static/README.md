This webviz instance has been automatically created from configuration file.

You can run it locally by running:

  cd THISFOLDER
  python3 ./webviz_app.py

If you want to upload it to e.g. Azure Container Registry, you can do e.g.

  cd THISFOLDER
  az acr build --registry $ACR_NAME --image $IMAGE_NAME . 

assuming you have set the environment variables $ACR_NAME and $IMAGE_NAME.
