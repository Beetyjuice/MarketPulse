#!/bin/bash

###############################################################################
# MarketPulse - Automated Startup Script
# Description: Automates the complete startup process for MarketPulse platform
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

###############################################################################
# Utility Functions
###############################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

###############################################################################
# Prerequisite Checks
###############################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker is installed"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "Docker Compose is installed"

    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    print_success "Docker daemon is running"

    # Check Python (optional, for local development)
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION is installed"
    else
        print_warning "Python3 not found (optional for local development)"
    fi
}

###############################################################################
# Environment Setup
###############################################################################

setup_environment() {
    print_header "Setting Up Environment"

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env file not found. Creating from .env.example..."
            cp .env.example .env
            print_success ".env file created"
            print_warning "Please review and update .env file with your API keys and configurations"

            # Ask user if they want to edit now
            read -p "Do you want to edit .env file now? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ${EDITOR:-nano} .env
            fi
        else
            print_error ".env.example not found. Cannot create .env file."
            print_info "Creating a basic .env file..."
            cat > .env << 'EOF'
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Cassandra Configuration
CASSANDRA_HOST=cassandra
CASSANDRA_PORT=9042

# API Keys (Please add your own)
ALPHA_VANTAGE_API_KEY=your_api_key_here
FINNHUB_API_KEY=your_api_key_here

# Environment
ENVIRONMENT=development
EOF
            print_success "Basic .env file created. Please update with your API keys."
        fi
    else
        print_success ".env file exists"
    fi
}

###############################################################################
# Docker Network Setup
###############################################################################

setup_network() {
    print_header "Setting Up Docker Network"

    # Check if network exists
    if docker network ls | grep -q "marketpulse-network"; then
        print_success "marketpulse-network already exists"
    else
        print_info "Creating marketpulse-network..."
        docker network create marketpulse-network
        print_success "marketpulse-network created"
    fi
}

###############################################################################
# Cleanup Old Containers
###############################################################################

cleanup_containers() {
    print_header "Cleaning Up Old Containers"

    read -p "Do you want to remove existing MarketPulse containers? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Stopping and removing old containers..."
        docker-compose -f docker-compose.enhanced.yml down 2>/dev/null || true
        print_success "Old containers removed"
    else
        print_info "Skipping container cleanup"
    fi
}

###############################################################################
# Start Services
###############################################################################

start_services() {
    print_header "Starting MarketPulse Services"

    print_info "This may take several minutes on first run (downloading images)..."

    # Pull latest images
    print_info "Pulling Docker images..."
    docker-compose -f docker-compose.enhanced.yml pull

    # Start services
    print_info "Starting services in detached mode..."
    docker-compose -f docker-compose.enhanced.yml up -d

    print_success "Services started successfully!"
}

###############################################################################
# Health Checks
###############################################################################

check_service_health() {
    print_header "Checking Service Health"

    print_info "Waiting for services to be ready (this may take 30-60 seconds)..."
    sleep 10

    # Check Kafka
    if docker ps | grep -q "marketpulse-kafka"; then
        print_success "Kafka is running"
    else
        print_warning "Kafka container not found"
    fi

    # Check Cassandra
    if docker ps | grep -q "marketpulse-cassandra"; then
        print_success "Cassandra is running"
    else
        print_warning "Cassandra container not found"
    fi

    # Check Spark
    if docker ps | grep -q "marketpulse-spark"; then
        print_success "Spark is running"
    else
        print_warning "Spark container not found"
    fi

    # Display all MarketPulse containers
    print_info "\nRunning MarketPulse containers:"
    docker ps --filter "name=marketpulse" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

###############################################################################
# Display Access Information
###############################################################################

display_access_info() {
    print_header "Access Information"

    echo -e "${GREEN}MarketPulse is now running!${NC}\n"

    echo -e "${BLUE}Dashboard:${NC}"
    echo -e "  • Main Dashboard: http://localhost:8501"
    echo -e "  • Enhanced Dashboard: http://localhost:8502\n"

    echo -e "${BLUE}Monitoring:${NC}"
    echo -e "  • Grafana: http://localhost:3000 (admin/admin)"
    echo -e "  • Prometheus: http://localhost:9090\n"

    echo -e "${BLUE}Services:${NC}"
    echo -e "  • Kafka: localhost:9092"
    echo -e "  • Cassandra: localhost:9042"
    echo -e "  • Spark Master: http://localhost:8080\n"

    echo -e "${BLUE}Useful Commands:${NC}"
    echo -e "  • View logs: ${YELLOW}docker-compose -f docker-compose.enhanced.yml logs -f${NC}"
    echo -e "  • Stop services: ${YELLOW}docker-compose -f docker-compose.enhanced.yml down${NC}"
    echo -e "  • Restart services: ${YELLOW}docker-compose -f docker-compose.enhanced.yml restart${NC}"
    echo -e "  • View status: ${YELLOW}docker-compose -f docker-compose.enhanced.yml ps${NC}\n"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
    __  ___           __        __  ____        __
   /  |/  /___ ______/ /_____  / /_/ __ \__  __/ /________
  / /|_/ / __ `/ ___/ //_/ _ \/ __/ /_/ / / / / / ___/ _ \
 / /  / / /_/ / /  / ,< /  __/ /_/ ____/ /_/ / (__  )  __/
/_/  /_/\__,_/_/  /_/|_|\___/\__/_/    \__,_/_/____/\___/

EOF
    echo -e "${NC}"
    echo -e "${BLUE}Morocco Stock Market AI Analysis Platform${NC}\n"

    # Execute setup steps
    check_prerequisites
    setup_environment
    setup_network
    cleanup_containers
    start_services
    check_service_health
    display_access_info

    print_success "\nMarketPulse startup complete!"
    print_info "Press Ctrl+C to view logs, or close this terminal."

    # Ask if user wants to view logs
    echo ""
    read -p "Do you want to view live logs? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f docker-compose.enhanced.yml logs -f
    fi
}

# Trap Ctrl+C
trap 'echo -e "\n${YELLOW}Startup interrupted by user${NC}"; exit 1' INT

# Run main function
main
