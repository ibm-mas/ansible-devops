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

# Create user and grant access
#-----------------------------------------------------------------------
resource "aws_iam_user" "user" {
  name = var.user_name
}

resource "aws_iam_access_key" "user" {
  user = aws_iam_user.user.name
}

resource "aws_iam_user_policy" "user" {
  name = "user_policy"
  user = aws_iam_user.user.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = var.perm_action
        Effect   = "Allow"
        Resource = var.perm_resources
      },
    ]
  })
}
