# Comprehensive MCP Server Catalog

This is a comprehensive list of MCP (Model Context Protocol) servers discovered for building the ultimate multicloud, multitool MCP server toolchest. These servers can be added to our MCP Hub to provide access to various databases, cloud platforms, marketing tools, documentation systems, and productivity applications.

## Currently Connected to Our Hub
- filesystem
- memory  
- sequential-thinking
- everything
- git
- time
- fetch
- database-insert
- github
- google-maps
- puppeteer

## Database MCP Servers

### Vector & Search Databases
- **Qdrant** - `qdrant/mcp-server-qdrant/` - Vector search engine for semantic memory layer
- **Elasticsearch** - `elastic/mcp-server-elasticsearch` - Query Elasticsearch data
- **Pinecone** - `pinecone-io/pinecone-mcp` - Vector database for AI applications
- **Meilisearch** - `meilisearch/meilisearch-mcp` - Full-text & semantic search API

### Relational Databases  
- **PostgreSQL** - `modelcontextprotocol/servers-archived/postgres` - Read-only database access with schema inspection
- **MySQL/MariaDB** - `mariadb/mcp` - Standard interface for MariaDB with SQL and vector search
- **SQLite** - `modelcontextprotocol/servers-archived/sqlite` - Database interaction and business intelligence
- **MCP Toolbox for Databases** - `googleapis/genai-toolbox` - Supports AlloyDB, BigQuery, Bigtable, Cloud SQL, MySQL, Postgres, Spanner

### Multi-Database JSON-RPC Processing
- **Database Insert Parser** - `mcp-server-db-insert` - Parse JSON-RPC responses and insert data into PostgreSQL, MongoDB, SQLite, Redis, and MySQL with automatic schema management, type conversion, and batch processing

### NoSQL & Document Databases
- **MongoDB** - `mongodb-js/mongodb-mcp-server` - Both Community Server and Atlas supported
- **Redis** - `redis/mcp-redis/` - Official Redis MCP server for key-value operations  
- **Redis Cloud API** - `redis/mcp-redis-cloud/` - Manage Redis Cloud resources
- **Astra DB** - `datastax/astra-db-mcp` - DataStax NoSQL database operations
- **Momento** - `momentohq/mcp-momento` - Cache for performance and cost optimization

### Graph Databases
- **Neo4j** - `neo4j-contrib/mcp-neo4j/` - Graph database with schema and cypher queries
- **Neo4j Agent Memory** - `knowall-ai/mcp-neo4j-agent-memory` - Memory management using knowledge graphs
- **Neo4j GDS** - `neo4j-contrib/gds-agent` - Graph data science with comprehensive algorithms
- **Memgraph** - `memgraph/ai-toolkit` - Query data in Memgraph graph database
- **Kuzu** - `kuzudb/kuzu-mcp-server` - Query execution on Kuzu graph database

### Time Series & Analytics
- **Apache IoTDB** - `apache/iotdb-mcp-server` - Time series database for IoT applications
- **Apache Doris** - `apache/doris-mcp-server` - MPP-based real-time data warehouse
- **ClickHouse** - `ClickHouse/mcp-clickhouse` - Query ClickHouse database server
- **GreptimeDB** - `GreptimeTeam/greptimedb-mcp-server` - Time-series database for observability
- **MotherDuck** - `motherduckdb/mcp-server-motherduck` - Query and analyze data with MotherDuck and DuckDB
- **Apache Pinot** - `startreedata/mcp-pinot` - Real-time analytics queries on Apache Pinot OLAP database
- **StarRocks** - `StarRocks/mcp-server-starrocks` - Interact with StarRocks analytics database
- **Teradata** - `Teradata/teradata-mcp-server` - Multi-task data analytics on Teradata platform

## Cloud Platform MCP Servers

### Amazon Web Services (AWS)
- **AWS** - `awslabs/mcp` - Specialized AWS MCP servers with best practices
- **AWS KB Retrieval** - `modelcontextprotocol/servers-archived/aws-kb-retrieval-server` - AWS Knowledge Base using Bedrock Agent Runtime

### Microsoft Azure
- **Azure** - `Azure/azure-mcp` - Access to key Azure services (Storage, Cosmos DB, Azure CLI)
- **Azure DevOps** - `microsoft/azure-devops-mcp` - Repositories, work items, builds, releases, test plans, code search

### Google Cloud Platform
- **Google Cloud (MCP Toolbox)** - `googleapis/genai-toolbox` - AlloyDB, BigQuery, Bigtable, Cloud SQL, Spanner

### Cloudflare
- **Cloudflare** - `cloudflare/mcp-server-cloudflare` - Deploy, configure & interrogate resources (Workers/KV/R2/D1)

### Alibaba Cloud
- **Alibaba Cloud AnalyticDB MySQL** - `aliyun/alibabacloud-adb-mysql-mcp-server`
- **Alibaba Cloud AnalyticDB PostgreSQL** - `aliyun/alibabacloud-adbpg-mcp-server` 
- **Alibaba Cloud DataWorks** - `aliyun/alibabacloud-dataworks-mcp-server`
- **Alibaba Cloud OpenSearch** - `aliyun/alibabacloud-opensearch-mcp-server`
- **Alibaba Cloud OPS** - `aliyun/alibaba-cloud-ops-mcp-server` - CloudOps Orchestration Service
- **Alibaba Cloud RDS** - `aliyun/alibabacloud-rds-openapi-mcp-server` - RDS resource management

### Multi-Cloud & Other Platforms
- **Aiven** - `Aiven-Open/mcp-aiven` - PostgreSQL, Kafka, ClickHouse, OpenSearch services
- **Supabase** - `supabase-community/supabase-mcp` - Create tables, query data, deploy edge functions
- **Tencent CloudBase** - `TencentCloudBase/CloudBase-AI-ToolKit` - Serverless functions and databases
- **Heroku** - `heroku/heroku-mcp-server` - Heroku Platform management (apps, add-ons, dynos, databases)
- **Terraform** - `hashicorp/terraform-mcp-server` - Infrastructure as Code (IaC) development
- **NanoVMs** - `nanovms/ops-mcp` - Build and deploy unikernels to any cloud

## Marketing & Advertising Platform MCP Servers

### Social Media & Professional Networks
- **LinkedIn MCP Runner** - `ertiqah/linkedin-mcp-runner` - Write, edit, and schedule LinkedIn posts via LiGo
- **LINE** - `line/line-bot-mcp-server` - Integrates LINE Messaging API to connect AI Agent to LINE Official Account

### Marketing Analytics & Insights
- **Audiense Insights** - `AudienseCo/mcp-audiense-insights` - Marketing insights and audience analysis from Audiense reports

### Productivity & Project Management (includes Monday.com via WayStation)
- **WayStation** - `waystation-ai/mcp` - Universal connector to Notion, **Monday**, AirTable and more productivity tools
- **Linear** - `linear.app/docs/mcp` - Search, create, and update Linear issues and projects

### Payment & E-commerce
- **PayPal** - `mcp.paypal.com/` - Official PayPal MCP server
- **Stripe** - `stripe/agent-toolkit` - Interact with Stripe API for payments
- **Razorpay** - `razorpay/razorpay-mcp-server` - Official Razorpay MCP server

### Universal Integration Platforms
- **Pipedream** - `PipedreamHQ/pipedream` - Connect with 2,500 APIs with 8,000+ prebuilt tools
- **Integration App** - `integration-app/mcp-server` - Interact with any SaaS applications on behalf of customers
- **Paragon ActionKit** - `useparagon/paragon-mcp` - Connect to 130+ SaaS integrations (Slack, Salesforce, Gmail)

## Documentation & Knowledge Management

### Official Platform Documentation
- **GitHub** - `github/github-mcp-server` - Official GitHub MCP server
- **Atlassian** - `atlassian.com/platform/remote-mcp-server` - Securely interact with Jira work items and Confluence pages

### Knowledge Base & Search
- **Perplexity** - `ppl-ai/modelcontextprotocol` - Real-time web-wide research API
- **Inkeep** - `inkeep/mcp-server-python` - RAG Search over your content
- **Ragie** - `ragieai/ragie-mcp-server/` - Retrieve context from RAG knowledge base (Google Drive, Notion, JIRA)
- **Needle** - `needle-ai/needle-mcp` - Production-ready RAG for document search and retrieval

## Messaging & Communication

### Team Communication
- **Slack** - `zencoderai/slack-mcp-server` - Channel management and messaging capabilities (community maintained)
- **Knock MCP Server** - `knocklabs/agent-toolkit` - Send messaging across email, in-app, push, SMS, Slack, MS Teams

### Email Services  
- **Mailgun** - `mailgun/mailgun-mcp-server` - Interact with Mailgun API
- **Mailjet** - `mailgun/mailjet-mcp-server` - Contact, campaign, segmentation, statistics, workflow APIs

## Development & DevOps Tools

### Version Control & CI/CD
- **GitKraken** - `gitkraken/gk-cli` - GitKraken APIs plus Jira, GitHub, GitLab integration
- **Buildkite** - `buildkite/buildkite-mcp-server` - Exposing Buildkite data (pipelines, builds, jobs, tests)
- **CloudBees** - `docs.cloudbees.com/docs/cloudbees-mcp/latest/` - Enable AI access to CloudBees Unify environment

### Monitoring & Observability
- **Dynatrace** - `dynatrace-oss/dynatrace-mcp` - Real-time observability and monitoring
- **Last9** - `last9/last9-mcp-server` - Real-time production context (logs, metrics, traces)
- **Logfire** - `pydantic/logfire-mcp` - Access to OpenTelemetry traces and metrics

## Web & Content Management

### Website Builders & CMS
- **Webflow** - `webflow/mcp-server` - Interact with Webflow sites, pages, and collections
- **Canva** - `canva.dev/docs/apps/mcp-server/` - AI-powered development assistance for Canva apps

### Web Services & APIs
- **WebScraping.AI** - `webscraping-ai/webscraping-ai-mcp-server` - Web data extraction and scraping
- **Brave Search** - `brave/brave-search-mcp-server` - Web and local search using Brave's Search API

## Authentication & Security

### Identity & Access Management
- **Auth0** - `auth0/auth0-mcp-server` - Tenant management for actions, applications, forms, logs
- **Asgardeo** - `asgardeo/asgardeo-mcp-server` - Interact with Asgardeo organization

### Security & Compliance
- **GitGuardian** - `GitGuardian/gg-mcp` - Scan projects for credential leaks with 500+ secret detectors
- **Endor Labs** - `endorlabs.com` - Find and fix security risks, scan for vulnerabilities and secret leaks

## Installation Commands

Most MCP servers can be installed using one of these methods:

### Using uvx (recommended)
```bash
uvx mcp-server-[SERVER_NAME]
```

### Using npm
```bash
npx @[ORGANIZATION]/[SERVER_NAME]
```

### Using Docker
```bash
docker run --rm -i [ORGANIZATION]/[SERVER_NAME]
```

### Configuration in Claude Desktop

Add servers to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "[server-name]": {
      "command": "uvx",
      "args": ["mcp-server-[server-name]", "[additional-args]"]
    }
  }
}
```

## Missing Platforms Still Needed

Based on the original request, we still need to find MCP servers for:
- **Google Ads** - Not found in current search
- **Google Tags/Google Tag Manager** - Not found in current search  
- **Meta Business Manager** - Not found in current search
- **Meta Ads (Facebook Ads)** - Not found in current search
- **TikTok Ads** - Not found in current search
- **Microsoft 365 Documentation** - Partial coverage via general Microsoft tools
- **Ubuntu Desktop Documentation** - Not found in current search

## Recommended Priority Servers to Add

Based on the multicloud, multitool strategy, I recommend adding these servers first:

1. **Universal Connectors**:
   - Pipedream (2,500 APIs, 8,000+ tools)
   - WayStation (Notion, Monday, AirTable, etc.)
   - Paragon ActionKit (130+ SaaS integrations)

2. **Database Essentials**:
   - MongoDB (mongodb-js/mongodb-mcp-server)
   - Qdrant (qdrant/mcp-server-qdrant/)
   - Redis (redis/mcp-redis/)
   - MCP Toolbox for Databases (googleapis/genai-toolbox)

3. **Major Cloud Platforms**:
   - AWS (awslabs/mcp)
   - Azure (Azure/azure-mcp)
   - Cloudflare (cloudflare/mcp-server-cloudflare)

4. **Essential Services**:
   - Stripe (stripe/agent-toolkit)
   - PayPal (mcp.paypal.com/)
   - Perplexity (ppl-ai/modelcontextprotocol)
   - LinkedIn MCP Runner (ertiqah/linkedin-mcp-runner)

This catalog represents the most comprehensive collection of MCP servers available as of now, providing access to virtually every major platform and service needed for a complete multicloud, multitool AI assistant ecosystem.
