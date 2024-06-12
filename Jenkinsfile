pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
    }

    stages {
        stage('Checkout') {
            steps {
                git credentialsId: 'github-credentials', url: 'https://github.com/Prathamesh78/AWS-ECR-Data-Pipeline.git', branch: 'main'
            }
        }

        stage('Terraform Init') {
            steps {
                dir('terraform') {
                    sh 'terraform init'
                }
            }
        }

        stage('Terraform Plan') {
            steps {
                dir('terraform') {
                    sh 'terraform plan -out=tfplan'
                }
            }
        }

        stage('Manual Approval') {
            steps {
                input 'Do you want to apply the Terraform changes?'
            }
        }

        stage('Terraform Apply') {
            steps {
                dir('terraform') {
                    sh 'terraform apply -parallelism=10 -auto-approve tfplan'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("aws-data-pipeline")
                }
            }
        }

        stage('Tag and Push to ECR') {
            steps {
                script {
                    sh '''
                        aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
                        docker tag aws-data-pipeline:latest public.ecr.aws/g2b9q7n9/aws-data-pipeline:latest
                        docker push public.ecr.aws/g2b9q7n9/aws-data-pipeline:latest
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
