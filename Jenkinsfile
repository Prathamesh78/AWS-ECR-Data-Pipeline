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
        DB_USER               = "admin"  
        DB_PASSWORD           = "Passw0rd!7810"
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

        stage('Fetch DB Host') {
            steps {
                script {
                    def rdsEndpoint = sh(script: 'terraform output -raw rds_endpoint', returnStdout: true).trim()
                    def rdsHost = rdsEndpoint.split(':')[0]
                    env.DB_HOST = rdsHost
                    echo "DB_HOST: ${env.DB_HOST}"
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

        stage('Building Images') {
            steps {
                script {
                    dockerImage = docker.build("${ECR_REPO_NAME}:${IMAGE_TAG}")
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
                    mysql -h ${env.DB_HOST} -u ${DB_USER} -p${DB_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};"
                    """
                }
            }
        }

        stage('Create Table') {
            steps {
                script {
                    sh """
                    mysql -h ${env.DB_HOST} -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} -e "
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
