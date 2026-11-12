
# ============================================================
# ROTA LIVRE - INFRAESTRUTURA AWS
# FIAP - Global Solution 2026.2
# Regiao: Estados Unidos (Ohio) - us-east-2
# ============================================================

# ------------------------------------------------------------
# 1. VPC PADRAO
# ------------------------------------------------------------

data "aws_vpc" "default" {
  default = true
}

# ------------------------------------------------------------
# 2. SUB-REDES DA VPC
# ------------------------------------------------------------

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ------------------------------------------------------------
# 3. IMAGEM AMAZON LINUX 2023
# ------------------------------------------------------------

data "aws_ssm_parameter" "amazon_linux" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# ------------------------------------------------------------
# 4. SECURITY GROUP
# ------------------------------------------------------------

resource "aws_security_group" "rota_livre" {
  name_prefix = "rota-livre-sg-"
  description = "Acesso publico HTTP ao ROTA LIVRE"
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Name = "rota-livre-security-group"
  }
}

# ------------------------------------------------------------
# 5. REGRAS DE ENTRADA
# ------------------------------------------------------------

# Permite HTTP publico para o MVP
resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.rota_livre.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 80
  to_port     = 80
  ip_protocol = "tcp"

  description = "Acesso HTTP publico ao MVP"
}

# SSH (porta 22) nao esta liberado.
# A API (porta 8000) tambem nao esta exposta publicamente.

# ------------------------------------------------------------
# 6. REGRAS DE SAIDA
# ------------------------------------------------------------

resource "aws_vpc_security_group_egress_rule" "outbound" {
  security_group_id = aws_security_group.rota_livre.id

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"

  description = "Conexoes de saida para downloads e AWS"
}

# ------------------------------------------------------------
# 7. INSTANCIA EC2
# ------------------------------------------------------------

locals {
  bootstrap = replace(file("${path.module}/bootstrap.sh"), "\r\n", "\n")
}

resource "aws_instance" "rota_livre" {
  # Sistema operacional
  ami           = data.aws_ssm_parameter.amazon_linux.value
  instance_type = "t3.small"

  # Rede
  subnet_id              = sort(data.aws_subnets.default.ids)[0]
  vpc_security_group_ids = [aws_security_group.rota_livre.id]

  # Permite acesso ao site pela internet
  associate_public_ip_address = true

  # Perfil IAM para AWS Systems Manager
  iam_instance_profile = aws_iam_instance_profile.rota_livre.name

  # Instala Docker e inicia o projeto automaticamente
  user_data = local.bootstrap

  user_data_replace_on_change = false

  lifecycle {
    prevent_destroy = true
    # Preserva a AMI e a subnet da instância existente quando as consultas mudam.
    ignore_changes = [ami, subnet_id]

    precondition {
      condition     = startswith(local.bootstrap, "#!/bin/bash\n")
      error_message = "O bootstrap deve começar com #!/bin/bash, sem BOM ou linha em branco."
    }
  }

  # Seguranca do servico de metadados
  metadata_options {
    http_tokens = "required"
  }

  # Disco criptografado
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "rota-livre-server"
  }
}

# ------------------------------------------------------------
# 8. OUTPUTS
# ------------------------------------------------------------

output "public_ip" {
  description = "IP publico da instancia ROTA LIVRE"
  value       = aws_instance.rota_livre.public_ip
}

output "public_url" {
  description = "Endereco HTTP publico do MVP ROTA LIVRE"
  value       = "http://${aws_instance.rota_livre.public_ip}"
}

output "instance_id" {
  description = "Identificador da instancia EC2"
  value       = aws_instance.rota_livre.id
}
