provider "aws" {
  region = "us-east-1"
}

resource "aws_ecr_repository" "repo" {
  name = "AWS-ECR-Data-Pipeline"
}

resource "aws_lambda_function" "function" {
  function_name = "aws-data-pipeline-function"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "app.main"
  image_uri     = "your-aws-account-id.dkr.ecr.your-region.amazonaws.com/aws-data-pipeline:latest"
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "policy-attachment" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
