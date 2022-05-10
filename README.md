![](server/artifacts/santiago.jpg)

# Predicting Apartment Renting Prices in Santiago, Chile

This data science project showcases a real estate price prediction study in Santiago (Chile). 
A Web Application displays the rent prices of apartments in Santiago, which are predicted 
by a machine learning model. 

The raw dataset containing the apartment listings (...) was extracted from the website https://www.portalinmobiliario.com/ 
through web scraping using `Selenium` and `BeautifulSoup`.  

This raw dataset was transformed through several stages of analysis, which are reported in several
jupyter notebooks located in the directory `model/`.
The first stage in this workflow was **Cleaning** the dataset and performing an **Exploratory Data Analysis (EDA)**, 
in order to get familiar with the data, handle NaN values, dealing with outliers and selecting the features which will be used 
for building a predictive model.
The next stage involved conducting **Feature Engineering** and implementing these transformations in a preprocessing pipeline
that was applied to the training and test sets extracted from original dataset.
Next, in the **Model Building** stage, various type of models, based on different algorithms, were trained to predict apartment 
rent prices, in a supervised regression learning task.
For each model type, the training was carried out applying a 5-fold cross validation on the training set, and performing 
hyperparameter optimization using `Optuna`.
Here the parameters of each model type, as well as all possible set of predictor features in the training set, were considered as 
hyperparameters to be optimized.
The following algorithms were used for model training:

- Multiple Regression
- LGBM Regressor
- XGBoost Regressor
- CatBoost Regressor

The best-performing trained models were then used to make predictions on the test set.
The model(s) that performed best on this evaluation was selected for deployment in our Web Application.

A final notebook presents a geospatial comparison of the **Model Predictions** made 
on the training and test sets by the selected model(s) for deployment.
Similar data distributions can be visualized as the different layers in the QGIS project 
stored in `qgis/home-prices-santiago.qgz`.

# Building Web Application for Predicting Prices of Apartments

The Web Application makes use of the selected model(s) to make predictions of the rent prices of 
apartments in Santiago and displays this information to the user.
Predicted rent prices are calculated based on the following fields which describe the desired apartment 
and need to be entered by the user: 
Apartment Surface (in square meters), Number of Bedrooms, Number of Bathrooms and Location (city).

The Web Application (see directory `app/`) is built in **JavaScript**, **HTML**, **CSS** and **Python**, using **Flask** 
as a web framework for development.
To overcome the intrinsic limitations of the **Flask's** built-in server, **Nginx** is used in deployment as a reverse proxy server 
to handle the http requests.

### TODO: include screenshot of dashboard

# Deploying Web Application to AWS Cloud (ECR, EC2, ECS)

## Containerizing Web Application:

We will deploy our Web Application to the **Amazon Web Services (AWS) Cloud**.
For this, we first build a docker image of our Web Application, based on the intructions 
contained in the Dockerfile stored in the root directory of our git repository.

```
docker build -t home-prices-santiago:1.0 .
```

If the image was created, it should appear in the listed shown after running:

```
docker images
```

We can now create the **Docker** container associated to our image by running:

```
docker run --network="host" -d home-prices-santiago:1.0
```

Here we added the "host" network option so that the the host (our local machine) network is 
accessible to the container...
If the container was correctly initialized, the **Flask** server should be also running.
We should be able to see this from the container logs:

```
docker logs <container_id>
```

And we should be able to see our Web Application by openning a browser at the URL address http://localhost.

## Pushing Docker image to AWS ECR:

Once we checked that our Web Application can be accessed from our local machine, we can start deploying it to AWS. 

In order to be able to push our **Docker** image to **AWS ECR (Elastic Container Registry)**, we need 
to authenticate the **Docker** CLI to our default registry, so that **Docker** can push and pull images with **AWS ECR**.
We do this as described in the **AWS** documentation (https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html):

```
aws ecr get-login-password --region <region> | docker login --username AWS \
    --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
```

Next, we create a repository in **AWS ECR**:

```
aws ecr create-repository --repository-name home-prices-santiago --region <region>
```

In order to push our **Docker** image, we need to tag the image that will be pushed to our **ECR** repository.

```
docker tag home-prices-santiago:1.0 <aws_account_id>.dkr.ecr.<region>.amazonaws.com/home-prices-santiago:latest
```

Finally, we push the **Docker** image to **ECR**:

```
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/home-prices-santiago:latest
```

## Deploying Docker container to AWS EC2, ECS:

Now, we will make use of the **AWS Command Line Interface** (CLI) tool to deploy the **Docker** image stored in **ECR** 
to a **EC2** instance in a **ECS (Elastic Container Service)** cluster.
First we need to create a security group that includes the traffic rules that we will allow for the **EC2** instance in 
our **ECS** cluster.

```
aws ec2 create-security-group --group-name hpsantiago-sg --description "security group for home-prices-santiago"

aws ec2 authorize-security-group-ingress --group-id <security_group_id> --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress --group-id <security_group_id> --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress --group-id <security_group_id> --protocol tcp --port 443 --cidr 0.0.0.0/0

```

Then we configure the **AWS ECS** CLI, by creating an **ECS** cluster and profile configurations as follows
(see documentation: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-cli-tutorial-ec2.html).

```
ecs-cli configure --cluster hpsantiago-cluster --default-launch-type EC2 \
    --config-name hpsantiago-cluster-config --region <region>
```

```
ecs-cli configure profile --profile-name hpsantiago-cluster-config-profile \
    --access-key <aws_access_key_id> --secret-key <aws_secret_access_key>
```

Once the configuration steps are done, we create the **ECS** cluster using the configurations defined above.

```
ecs-cli up --capability-iam --keypair <keypair_name> --size 1 --instance-type t2.micro \
    --cluster-config hpsantiago-cluster-config --ecs-profile hpsantiago-cluster-config-profile \
    --security-group <security_group_ids> --vpc <vpc_id> --subnets <subnet_1_id,subnet_2_id> --verbose
```

Here `<vpc_id>` can be obtained from: `aws ec2 describe-security-groups --group-id <security_group_id>`.
While `<subnet_1_id,subnet_2_id>` are the ids of the two subnets associated to `<vpc_id>` found from:
`aws ec2 describe-subnets` 

After a few minutes, we should have our **ECS** cluster up and running, and we can deploy our **Docker** container into it.
We can define this deployment as a registered task, which we then run and use to create a service for the defined task.
The following commands perform these deployment steps:

```
aws ecs register-task-definition --cli-input-json file:///<path>/home-prices-santiago/deploy/aws_ecs_task_definition.json

aws ecs run-task --cli-input-json file:///<path>/home-prices-santiago/deploy/aws_ecs_task_run.json

aws ecs create-service --cli-input-json file:///<path>/home-prices-santiago/deploy/aws_ecs_service.json
```

From the **AWS Console**, we should now be able to see that the defined task and service are running.
Alternatively, we run the following commands to obtain the same information:

```
aws ecs list-tasks --cluster hpsantiago-cluster
aws ecs list-services --cluster hpsantiago-cluster
```

After confirming it, we will be able to inspect our Web Application by openning a browser under the Public DNS URL provided 
for our **EC2** instance.

In this case, the Web Application is accessible under the following URL:
http://ec2-3-17-55-191.us-east-2.compute.amazonaws.com/
