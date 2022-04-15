variable "region" {
  type = string
}

variable "openshift_api" {
  type = string
}

variable "openshift_username" {
  type = string
}

variable "openshift_password" {
  type = string
}

variable "openshift_token" {
  type        = string
  description = "For cases where you don't have the password but a token can be generated (e.g SSO is being used)"
  sensitive = true
}

variable "installer_workspace" {
  type        = string
  description = "Folder to store/find the installation files"
}

variable "aws_amis" {
  default = {
    "af-south-1": {
        "hvm": "ami-0401d6ad383dba55c"
    },
    "ap-east-1": {
        "hvm": "ami-03ac23c984c812cb4"
    },
    "ap-northeast-1": {
        "hvm": "ami-09cc1da8a6fa42c4e"
    },
    "ap-northeast-2": {
        "hvm": "ami-0adf87370198caaed"
    },
    "ap-northeast-3": {
        "hvm": "ami-0591a1337ebe93646"
    },
    "ap-south-1": {
        "hvm": "ami-08dfa06820a4fb482"
    },
    "ap-southeast-1": {
        "hvm": "ami-05345a132d89bd2b6"
    },
    "ap-southeast-2": {
        "hvm": "ami-00274925d47c6e015"
    },
    "ca-central-1": {
        "hvm": "ami-0baeff23c4cc6ddf5"
    },
    "eu-central-1": {
        "hvm": "ami-083ab4c282bac44b5"
    },
    "eu-north-1": {
        "hvm": "ami-0791daa430c70ff09"
    },
    "eu-south-1": {
        "hvm": "ami-093ccc9e024810fc8"
    },
    "eu-west-1": {
        "hvm": "ami-07323d56fb932c84c"
    },
    "eu-west-2": {
        "hvm": "ami-0cabefac75acfd8e3"
    },
    "eu-west-3": {
        "hvm": "ami-01f9af256e3213df9"
    },
    "me-south-1": {
        "hvm": "ami-0e5d014111ee32e16"
    },
    "sa-east-1": {
        "hvm": "ami-0dd8411ece8c06dae"
    },
    "us-east-1": {
        "hvm": "ami-03d1c2cba04df838c"
    },
    "us-east-2": {
        "hvm": "ami-0ddab715d6b88a315"
    },
    "us-west-1": {
        "hvm": "ami-09b797de07577bf33"
    },
    "us-west-2": {
        "hvm": "ami-0617611237b58ac93"
    }
  }
}

variable "ocs" {
  default = {
    enable = true
    ami_id = ""
    dedicated_nodes = true
    dedicated_node_instance_type = "m5.4xlarge"
    dedicated_node_zones = []
    dedicated_node_subnet_ids = []
  }
}