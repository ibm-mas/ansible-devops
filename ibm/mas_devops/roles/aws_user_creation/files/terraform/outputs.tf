/*
Outputs for service credentials Read Write
*/
output "user_arn" {
  value = aws_iam_user.user.arn
}

output "user_access_key_id" {
  value = aws_iam_access_key.user.id
}

output "user_secret_access_key" {
  value = aws_iam_access_key.user.secret
}
