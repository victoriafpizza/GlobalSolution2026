
# Permissao para a EC2 utilizar o AWS Systems Manager

data "aws_iam_policy_document" "ec2_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "rota_livre_ssm" {
  name               = "rota-livre-ec2-ssm"
  assume_role_policy = data.aws_iam_policy_document.ec2_trust.json
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.rota_livre_ssm.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "rota_livre" {
  name = "rota-livre-instance-profile"
  role = aws_iam_role.rota_livre_ssm.name
}
