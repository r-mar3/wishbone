## Overview

| Component | Folder | Description |
|-----------|------|-------------|
| **NUMBER ECR** | `ecr` | Creation of ECRs for holding the images |
|**Dashboard ECS**|`ecs`| ECS to run the dashboard off|
| **Email Alert Lambda** | `email_lambda` | Lambda function to send out emails |
| **ETL Lambda** | `etl_lambda` | Lambda to run the ETL pipeline |
| **S3 Glue Crawler** | `glue_crawler` | Glue crawler to update historical database | 
| **Price history lambda** | `price_history_lambda` | Lambda that deletes from RDS all game data that is not from the current day |
|**Wishbone RDS**|`rds`| RDS to hold live data |
| **Historical S3** | `s3` | S3 to hold historical data |
| **Email Tracking Lambda** | `tracking_lambda` | Lambda to add new emails to the tracking table |

### 'Lambda' Folders:
These require the ECRs that they pull from to contain an image before being created, otherwise an error will be returned. 
Each of these require secrets for RDS, AWS and S3 credentials held in variables.tf and terraform.tfvars files

### How to run:

Each folder is a separate Terraform directory, so each requires the terminal command 'terraform init' before running 'terraform apply'. This was built in a modular fashion, so each directory contains the variables.tf and terraform.tfvars files requried for creating each resource. 

#### Order of execution:
- RDS, S3 and ECR created first. This can then be followed by each of the Lambda directories once the ECRs have images pushed up to them. 
---


