provider "aws" {
  region     = var.region
  access_key = var.access_key_id
  secret_key = var.secret_access_key
}

resource "aws_security_group" "masocp-bastion-host-sg" {
  name = "masocp-${var.unique_str}-bastion-host-sg"
  vpc_id = var.vpc_id
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    protocol = "-1"
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "masocp-${var.unique_str}-bastion-host-sg"
  }
}

data "aws_instance" "bootnode_details"{
filter {
  name = "tag:Name"
  values =["masocp-${var.unique_str}-bootnode"]
  }
}

resource "aws_instance" "masocp-bastion-host" {
  ami = data.aws_instance.bootnode_details.ami
  instance_type = "t3.micro"
  associate_public_ip_address = true
  subnet_id = var.subnet_id
  key_name = var.key_name
  security_groups = [aws_security_group.masocp-bastion-host-sg.id]
  iam_instance_profile = var.iam_instance_profile
  user_data = var.user_data
  tags = {
    Name = "masocp-${var.unique_str}-bastion-host"
  }
}
