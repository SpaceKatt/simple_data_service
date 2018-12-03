variable "region" {
  type = "string"

  default = "us-west-2"
}

provider "aws" {
  region = "${var.region}"
}

resource "aws_key_pair" "simple-data-auto" {
    key_name = "simple-data-auto"
    public_key = "${file("../../private/id_terra.pub")}"
}

variable "simple-data-service-ami" {}

resource "aws_default_vpc" "default" {}

resource "aws_security_group" "simple-data-sg" {
  name   = "simple-data-group"
  vpc_id = "${aws_default_vpc.default.id}"

  ingress {
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 5432
    to_port     = 5432
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "tcp"
    from_port   = 5432
    to_port     = 5432
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "simple-data" {
  ami                         = "${var.simple-data-service-ami}"
  instance_type               = "t2.micro"
  security_groups             = ["${aws_security_group.simple-data-sg.name}"]
  associate_public_ip_address = true
  key_name = "${aws_key_pair.simple-data-auto.key_name}"

  connection {
    user = "ubuntu"
    private_key = "${file("../../private/terraform-packer-example.pem")}"
  }

  provisioner "file" {
    source = "../../private/credentials"
    destination = "/home/ubuntu/.aws/credentials"
  }

  provisioner "file" {
    source = "../../private/config"
    destination = "/home/ubuntu/.aws/config"
  }

  provisioner "file" {
    source = "../../.env"
    destination = "/home/ubuntu/.env"
  }
}

output "instance_ips" {
  value = ["${aws_instance.simple-data.public_ip}"]
}
