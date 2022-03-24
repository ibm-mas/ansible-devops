output "vpcid" {
  value = aws_vpc.cpdvpc.id
}

output "master_subnet1_id" {
  value = aws_subnet.master1.id
}

output "master_subnet2_id" {
  value = aws_subnet.master2[*].id
}

output "master_subnet3_id" {
  value = aws_subnet.master3[*].id
}

output "worker_subnet1_id" {
  value = aws_subnet.worker1.id
}

output "worker_subnet2_id" {
  value = aws_subnet.worker2[*].id
}

output "worker_subnet3_id" {
  value = aws_subnet.worker3[*].id
}
