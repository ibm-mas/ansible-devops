/*
Reusable and configurable Openshift module
*/

# Terraform Backend configurations
# Note: variables are not allowed in this configuration block
terraform {
  backend "s3" {
    skip_region_validation = true
    skip_credentials_validation = true
    skip_metadata_api_check = true
  }
}

#2. Create Access Point
#-----------------------------------------------------------------------
resource "aws_s3_access_point" "bucket" {
  bucket = var.bucket_name
  name   = var.access_point_name
}

resource "aws_s3control_access_point_policy" "example" {
  access_point_arn = aws_s3_access_point.bucket.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = var.perm_action
      Principal = {
        AWS = var.user_arn
      }
      Resource = ["${aws_s3_access_point.bucket.arn}/object/*","${aws_s3_access_point.bucket.arn}"]
      
    }]
  })
}
