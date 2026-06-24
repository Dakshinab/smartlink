terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
}

provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

variable "tenancy_ocid"        {}
variable "user_ocid"           {}
variable "fingerprint"         {}
variable "private_key_path"    {}
variable "compartment_ocid"    {}
variable "ssh_public_key_path" {}
variable "region"              { default = "ap-singapore-1" }

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

data "oci_core_images" "ubuntu" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "22.04"
  shape                    = "VM.Standard.E5.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_vcn" "smartlink_vcn" {
  compartment_id = var.compartment_ocid
  cidr_block     = "10.0.0.0/16"
  display_name   = "smartlink-vcn"
}

resource "oci_core_internet_gateway" "smartlink_igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.smartlink_vcn.id
  display_name   = "smartlink-igw"
  enabled        = true
}

resource "oci_core_route_table" "smartlink_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.smartlink_vcn.id
  display_name   = "smartlink-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.smartlink_igw.id
  }
}

resource "oci_core_security_list" "smartlink_sl" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.smartlink_vcn.id
  display_name   = "smartlink-sl"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      max = 22
      min = 22
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      max = 80
      min = 80
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      max = 443
      min = 443
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      max = 5001
      min = 5001
    }
  }
}

resource "oci_core_subnet" "smartlink_subnet" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.smartlink_vcn.id
  cidr_block        = "10.0.1.0/24"
  display_name      = "smartlink-subnet"
  route_table_id    = oci_core_route_table.smartlink_rt.id
  security_list_ids = [oci_core_security_list.smartlink_sl.id]
}

resource "oci_core_instance" "smartlink_vm" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "smartlink-server"

  shape = "VM.Standard.E5.Flex"
  shape_config {
    ocpus         = 1
    memory_in_gbs = 12
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.smartlink_subnet.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = file(var.ssh_public_key_path)
    user_data           = base64encode(<<-EOF
      #!/bin/bash
      apt-get update -y
      apt-get install -y docker.io docker-compose-v2
      systemctl start docker
      systemctl enable docker
      usermod -aG docker ubuntu
    EOF
    )
  }
}

output "server_public_ip" {
  value       = oci_core_instance.smartlink_vm.public_ip
  description = "SSH into your server using this IP"
}