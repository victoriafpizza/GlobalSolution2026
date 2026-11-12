
# ROTA LIVRE - Infraestrutura AWS

# Utiliza a VPC padrao existente na regiao Ohio
data "aws_vpc" "default" {
  default = true
}

# Identifica as sub-redes disponiveis
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Consulta a imagem Amazon Linux 2023
data "aws_ssm_parameter" "amazon_linux" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# Grupo de seguranca
resource "aws_security_group" "rota_livre" {
  name_prefix = "rota-livre-sg-"
  description = "Acesso publico HTTP ao ROTA LIVRE"
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Name = "rota-livre-security-group"
  }
}

# Permite acesso HTTP publico
resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.rota_livre.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
  description       = "Acesso HTTP publico ao MVP"
}

# Permite conexoes de saida
resource "aws_vpc_security_group_egress_rule" "outbound" {
  security_group_id = aws_security_group.rota_livre.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  description       = "Conexoes de saida"
}

# Servidor da aplicacao
resource "aws_instance" "rota_livre" {
  ami                    = data.aws_ssm_parameter.amazon_linux.value
  instance_type          = "t3.small"
  subnet_id              = sort(data.aws_subnets.default.ids)[0]
  vpc_security_group_ids = [aws_security_group.rota_livre.id]

  associate_public_ip_address = true

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "rota-livre-server"
  }
}

output "public_ip" {
  description = "IP publico do servidor ROTA LIVRE"
  value       = aws_instance.rota_livre.public_ip
}
