provider "aws" {
    region = "us-east-1"  
}

resource "aws_s3_bucket" "bucket"{
  bucket = "prathameshs3bucket7810"

  tags = {
    Name = "My Bucket"
  }
}

resource "aws_s3_object" "file" {
  bucket = aws_s3_bucket.bucket.id
  key = "customers.csv"
  source = "customers.csv"
}

resource "aws_db_instance" "myrds" {
    allocated_storage   = var.dbstorage
   storage_type        = "gp2"
   identifier          = "rdstf"
   engine              = "mysql"
   engine_version      = "8.0.35"
   instance_class      = "db.t3.micro"
   username            = "admin"
   password            = "Passw0rd!7810"
   publicly_accessible = true
   skip_final_snapshot = true

   tags = {
     Name = "MyRDS"
   }
 }

resource "aws_ecr_repository" "repo" {
  name = "s3-to-rds"

  image_scanning_configuration {
    scan_on_push = true
  }
}

output "s3_bucket_name" {
  value = aws_s3_bucket.bucket.bucket
}

output "rds_endpoint" {
  value = aws_db_instance.myrds.endpoint
}

output "rds_db_name" {
  value = aws_db_instance.myrds.db_name
}

output "rds_username" {
  value = aws_db_instance.myrds.username
}

output "rds_password" {
  value = aws_db_instance.myrds.password
  sensitive = true
}

output "ecr_repository_url" {
  value = aws_ecr_repository.repo.repository_url
}

variable "dbstorage" {
  default = 20
}
