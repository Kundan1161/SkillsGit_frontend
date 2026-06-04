---
id: skillsgit-curated/imported-google-skills-cloud-sql-basics
version: 1.0.0
name: Cloud SQL Basics
description: Provision and manage Cloud SQL instances and databases for MySQL, PostgreSQL, or SQL Server with backups, HA, and secure connectivity.
authors:
  - name: Google (original)
    handle: google
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: data
tags: [imported, source-google, gcp, cloud-sql, postgres, mysql, sqlserver]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gemini-2.0-pro]
trigger_keywords: [cloud sql, postgres instance, mysql instance, cloud sql proxy, gcloud sql]
example_invocations:
  - "Create a Cloud SQL for PostgreSQL instance."
  - "Connect to a Cloud SQL instance via the Auth Proxy."
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from google/skills under Apache-2.0.
---

# Cloud SQL Basics

## When to use

Use this skill when the user asks to create or manage a Cloud SQL instance or database for MySQL, PostgreSQL, or SQL Server. Cloud SQL handles backups, high availability, and secure connectivity for relational database workloads.

## How to apply

Enable the SQL Admin API, create an instance with the desired engine, set the default user's password, create a database, retrieve the connection name, and connect through the Cloud SQL Auth Proxy.

## Overview

Cloud SQL is a fully managed relational database service for MySQL, PostgreSQL, and SQL Server. It automates time-consuming tasks like patches, updates, backups, and replicas, while providing high performance and availability for your applications.

## Prerequisites

Ensure you have the necessary IAM permissions to create and manage Cloud SQL instances. The Cloud SQL Admin (`roles/cloudsql.admin`) role provides full access to Cloud SQL resources.

## Quick Start (PostgreSQL)

1. Enable the API:
   ```bash
   gcloud services enable sqladmin.googleapis.com --quiet
   ```

2. Create an Instance:
   ```bash
   gcloud sql instances create INSTANCE_NAME \
     --database-version=POSTGRES_18 \
     --cpu=2 \
     --memory=7680MiB \
     --region=REGION \
     --quiet
   ```

3. Set a password for the default user (`postgres` for PostgreSQL):
   ```bash
   gcloud sql users set-password postgres \
     --instance=INSTANCE_NAME --password=PASSWORD \
     --quiet
   ```

4. Create a database:
   ```bash
   gcloud sql databases create DATABASE_NAME \
     --instance=INSTANCE_NAME \
     --quiet
   ```

5. Get the instance connection name (`PROJECT_ID:REGION:INSTANCE_NAME`):
   ```bash
   gcloud sql instances describe INSTANCE_NAME \
     --format="value(connectionName)" \
     --quiet
   ```

6. Connect via the Cloud SQL Auth Proxy:
   ```bash
   ./cloud-sql-proxy INSTANCE_CONNECTION_NAME
   ```
   Then in another terminal:
   ```bash
   psql "host=127.0.0.1 port=5432 user=postgres dbname=DATABASE_NAME password=PASSWORD sslmode=disable"
   ```

## Reference Directory

- Core Concepts: instance architecture, high availability (HA), supported database engines.
- CLI Usage: essential `gcloud sql` commands for instance, database, and user management.
- Client Libraries and Connectors: connecting from Python, Java, Node.js, and Go.
- MCP Usage: Cloud SQL remote MCP server and Gemini CLI extension.
- Infrastructure as Code: Terraform configuration for instances, databases, and users.
- IAM and Security: predefined roles, SSL/TLS certificates, and Auth Proxy configuration.

If you need product information not found in these references, use the Developer Knowledge MCP server `search_documents` tool.

## Attribution

This skill was imported from `google/skills` under the Apache-2.0 license. Original content authored by Google. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections; addition of `## When to use` and `## How to apply` stubs required by our validator. The original LICENSE and NOTICE files are preserved at the source repository.

## Sources reviewed

- https://github.com/google/skills/tree/main/skills/cloud/cloud-sql-basics (Apache-2.0)
