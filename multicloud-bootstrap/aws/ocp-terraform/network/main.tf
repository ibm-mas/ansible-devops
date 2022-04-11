resource "aws_vpc" "cpdvpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  instance_tenancy     = var.tenancy

  tags = {
    Name = "${var.network_tag_prefix}-vpc"
  }
}

resource "aws_internet_gateway" "master" {
  vpc_id = aws_vpc.cpdvpc.id
}

resource "aws_subnet" "master1" {
  vpc_id                  = aws_vpc.cpdvpc.id
  cidr_block              = var.master_subnet_cidr1
  availability_zone       = var.availability_zone1
  map_public_ip_on_launch = true
  depends_on              = [aws_internet_gateway.master]

  tags = {
    "Name" : join("-", [var.network_tag_prefix, "cpd-public-subnet", var.availability_zone1])
  }
}
resource "aws_subnet" "master2" {
  count                   = var.az == "multi_zone" ? 1 : 0
  vpc_id                  = aws_vpc.cpdvpc.id
  cidr_block              = var.master_subnet_cidr2
  availability_zone       = var.availability_zone2
  map_public_ip_on_launch = true
  depends_on              = [aws_internet_gateway.master]

  tags = {
    "Name" : join("-", [var.network_tag_prefix, "cpd-public-subnet", var.availability_zone2])
  }
}
resource "aws_subnet" "master3" {
  count                   = var.az == "multi_zone" ? 1 : 0
  vpc_id                  = aws_vpc.cpdvpc.id
  cidr_block              = var.master_subnet_cidr3
  availability_zone       = var.availability_zone3
  map_public_ip_on_launch = true
  depends_on              = [aws_internet_gateway.master]

  tags = {
    "Name" : join("-", [var.network_tag_prefix, "cpd-public-subnet", var.availability_zone3])
  }
}

resource "aws_route_table" "master" {
  vpc_id = aws_vpc.cpdvpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.master.id
  }
}

resource "aws_route_table_association" "master1" {
  subnet_id      = aws_subnet.master1.id
  route_table_id = aws_route_table.master.id
}
resource "aws_route_table_association" "master2" {
  count          = var.az == "multi_zone" ? 1 : 0
  subnet_id      = aws_subnet.master2[0].id
  route_table_id = aws_route_table.master.id
}
resource "aws_route_table_association" "master3" {
  count          = var.az == "multi_zone" ? 1 : 0
  subnet_id      = aws_subnet.master3[0].id
  route_table_id = aws_route_table.master.id
}

resource "aws_eip" "eip1" {
  vpc = true

  depends_on = [
    aws_vpc.cpdvpc,
  ]
}
resource "aws_eip" "eip2" {
  count = var.az == "multi_zone" ? 1 : 0
  vpc   = true

  depends_on = [
    aws_vpc.cpdvpc,
  ]
}
resource "aws_eip" "eip3" {
  count = var.az == "multi_zone" ? 1 : 0
  vpc   = true

  depends_on = [
    aws_vpc.cpdvpc,
  ]
}
resource "aws_nat_gateway" "nat1" {
  allocation_id = aws_eip.eip1.id
  subnet_id     = aws_subnet.master1.id
}
resource "aws_nat_gateway" "nat2" {
  count         = var.az == "multi_zone" ? 1 : 0
  allocation_id = aws_eip.eip2[0].id
  subnet_id     = aws_subnet.master2[0].id
}
resource "aws_nat_gateway" "nat3" {
  count         = var.az == "multi_zone" ? 1 : 0
  allocation_id = aws_eip.eip3[0].id
  subnet_id     = aws_subnet.master3[0].id
}
resource "aws_subnet" "worker1" {
  vpc_id            = aws_vpc.cpdvpc.id
  cidr_block        = var.worker_subnet_cidr1
  availability_zone = var.availability_zone1
  depends_on        = [aws_nat_gateway.nat1]

  tags = {
    "Name" : join("-", [var.network_tag_prefix, "cpd-private-subnet", var.availability_zone1])
  }
}
resource "aws_subnet" "worker2" {
  count             = var.az == "multi_zone" ? 1 : 0
  vpc_id            = aws_vpc.cpdvpc.id
  cidr_block        = var.worker_subnet_cidr2
  availability_zone = var.availability_zone2
  depends_on        = [aws_nat_gateway.nat2]

  tags = {
    "Name" : join("-", [var.network_tag_prefix, "cpd-private-subnet", var.availability_zone2])
  }
}
resource "aws_subnet" "worker3" {
  count             = var.az == "multi_zone" ? 1 : 0
  vpc_id            = aws_vpc.cpdvpc.id
  cidr_block        = var.worker_subnet_cidr3
  availability_zone = var.availability_zone3
  depends_on        = [aws_nat_gateway.nat3]

  tags = {
    "Name" : join("-", [var.network_tag_prefix, "cpd-private-subnet", var.availability_zone3])
  }
}
resource "aws_route_table" "worker1" {
  vpc_id = aws_vpc.cpdvpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_nat_gateway.nat1.id
  }
}
resource "aws_route_table" "worker2" {
  count  = var.az == "multi_zone" ? 1 : 0
  vpc_id = aws_vpc.cpdvpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_nat_gateway.nat2[0].id
  }
}
resource "aws_route_table" "worker3" {
  count  = var.az == "multi_zone" ? 1 : 0
  vpc_id = aws_vpc.cpdvpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_nat_gateway.nat3[0].id
  }
}
resource "aws_route_table_association" "privateroute1" {
  subnet_id      = aws_subnet.worker1.id
  route_table_id = aws_route_table.worker1.id
}
resource "aws_route_table_association" "privateroute2" {
  count          = var.az == "multi_zone" ? 1 : 0
  subnet_id      = aws_subnet.worker2[0].id
  route_table_id = aws_route_table.worker2[0].id
}
resource "aws_route_table_association" "privateroute3" {
  count          = var.az == "multi_zone" ? 1 : 0
  subnet_id      = aws_subnet.worker3[0].id
  route_table_id = aws_route_table.worker3[0].id
}
/*
This security group allows intra-node communication on all ports with all
protocols.
*/
resource "aws_security_group" "openshift-vpc" {
  name        = "${var.network_tag_prefix}-openshift-vpc"
  description = "Default security group that allows all instances in the VPC to talk to each other over any port and protocol."
  vpc_id      = aws_vpc.cpdvpc.id
  ingress {
    from_port = "0"
    to_port   = "0"
    protocol  = "-1"
    self      = true
  }
  egress {
    from_port = "0"
    to_port   = "0"
    protocol  = "-1"
    self      = true
  }
}