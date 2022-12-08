# /*
# Outputs for Bucket module
# */
output "alias" {
  value = aws_s3_access_point.bucket.alias
}

output "arn" {
  value = aws_s3_access_point.bucket.arn
}

output "endpoints" {
  value = aws_s3_access_point.bucket.endpoints
}

output "domain_name" {
  value = aws_s3_access_point.bucket.domain_name
}

output "id" {
  value = aws_s3_access_point.bucket.id
}
