pipeline {
    agent any

    parameters {
        booleanParam(name: 'autoApprove', defaultValue: false, description: 'Automatically run apply after generating plan?')
    }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        AWS_ACCOUNT_ID        = "891377100011"
        AWS_DEFAULT_REGION    = "us-east-1"
        ECR_REPO_NAME         = "s3-to-rds"
        IMAGE_TAG             = "latest"
        REPOSITORY_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}"
        DB_NAME               = "mydatabase"
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main', url: 'https://github.com/Prathamesh78/AWS-Data_Pipeline.git'
                }
            }
        }

        stage('Terraform Init') {
            steps {
                script {
                    sh 'terraform init'
                }
            }
        }

        stage('Terraform Plan') {
            steps {
                script {
                    sh 'terraform plan -out=tfplan'
                    sh 'terraform show -no-color tfplan > tfplan.txt'
                }
            }
        }

        stage('Approval') {
            when {
                not {
                    equals expected: true, actual: params.autoApprove
                }
            }

            steps {
                script {
                    def plan = readFile 'tfplan.txt'
                    input message: "Do you want to apply the plan?",
                          parameters: [text(name: 'Plan', description: 'Please review the plan', defaultValue: plan)]
                }
            }
        }

        stage('Terraform Apply') {
            steps {
                script {
                    sh 'terraform apply -input=false tfplan'
                }
            }
        }

        stage('Fetch DB Credentials and S3 URI') {
            steps {
                script {
                    def rdsEndpoint = sh(script: 'terraform output -raw rds_endpoint', returnStdout: true).trim()
                    def rdsHost = rdsEndpoint.split(':')[0]
                    env.DB_HOST = rdsHost

                    env.DB_USER = sh(script: 'terraform output -raw rds_username', returnStdout: true).trim()
                    env.DB_PASSWORD = sh(script: 'terraform output -raw rds_password', returnStdout: true).trim()

                    def s3Bucket = sh(script: 'terraform output -raw s3_bucket_name', returnStdout: true).trim()
                    def s3Uri = "s3://${s3Bucket}/customers.csv"
                    env.S3_URI = s3Uri

                    echo "DB_HOST: ${env.DB_HOST}"
                    echo "DB_USER: ${env.DB_USER}"
                    echo "DB_PASSWORD: ${env.DB_PASSWORD}"
                    echo "S3_URI: ${env.S3_URI}"
                }
            }
        }

        stage('Logging into AWS ECR') {
            steps {
                script {
                    sh 'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $REPOSITORY_URL'
                }
            }
        }

        stage('Building Image') {
            steps {
                script {
                    dockerImage = docker.build("${ECR_REPO_NAME}:${IMAGE_TAG}", 
                        "--build-arg S3_URI=${env.S3_URI} --build-arg SQL_HOST=${env.DB_HOST} --build-arg SQL_USER=${env.DB_USER} --build-arg SQL_PASSWORD=${env.DB_PASSWORD} --build-arg AWS_ACCESS_KEY_ID=${env.AWS_ACCESS_KEY_ID} --build-arg AWS_SECRET_ACCESS_KEY=${env.AWS_SECRET_ACCESS_KEY} .")
                }
            }
        }

        stage('Push to ECR') {
            steps {
                script {
                    sh "docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${REPOSITORY_URL}:${IMAGE_TAG}"
                    sh "docker push ${REPOSITORY_URL}:${IMAGE_TAG}"
                }
            }
        }

        stage('Create Database') {
            steps {
                script {
                    sh """
                    mysql -h ${env.DB_HOST} -u ${env.DB_USER} -p${env.DB_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};"
                    """
                }
            }
        }

        stage('Create Table') {
            steps {
                script {
                    sh """
                    mysql -h ${env.DB_HOST} -u ${env.DB_USER} -p${env.DB_PASSWORD} ${DB_NAME} -e "
                    CREATE TABLE IF NOT EXISTS customers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        city VARCHAR(255),
                        country VARCHAR(255)
                    );
                    "
                    """
                }
            }
        }

        stage('Create ECS') {
            steps {
                script {
                    sh "aws ecs register-task-definition --region $AWS_DEFAULT_REGION --cli-input-json file://task_definition.json"
                }
            }
        }
        
        stage('Create Lambda Function') {
            steps {
                script {
                    sh """
                    aws lambda create-function \
                        --function-name s3-rds-function \
                        --package-type Image \
                        --code ImageUri=${REPOSITORY_URL}:${IMAGE_TAG} \
                        --role arn:aws:iam::891377100011:role/lambda_exec_role \
                        --region ${AWS_DEFAULT_REGION}
                    """
                }
            }
        }

        stage('Test Lambda Function') {
            steps {
                script {
                    sh """
                    aws lambda invoke \
                        --function-name s3-rds-function \
                        --payload '{}' \
                        output.json
                    """
                    def output = readFile 'output.json'
                    echo "Lambda output: ${output}"
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
