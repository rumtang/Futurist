#!/bin/bash

# Docker Configuration Validation Script
# Tests Docker builds and basic functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker status..."
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_success "Docker is running"
}

# Validate Dockerfiles
validate_dockerfiles() {
    print_status "Validating Dockerfiles..."
    
    # Check production Dockerfiles
    if [ -f "Dockerfile" ]; then
        print_status "Validating backend production Dockerfile..."
        docker build -f Dockerfile -t cx-futurist-api:test . --target builder
        print_success "Backend production Dockerfile is valid"
    else
        print_error "Backend production Dockerfile not found"
        return 1
    fi
    
    if [ -f "frontend/Dockerfile" ]; then
        print_status "Validating frontend production Dockerfile..."
        docker build -f frontend/Dockerfile -t cx-futurist-frontend:test frontend/ --target builder
        print_success "Frontend production Dockerfile is valid"
    else
        print_error "Frontend production Dockerfile not found"
        return 1
    fi
    
    # Check development Dockerfiles
    if [ -f "Dockerfile.dev" ]; then
        print_status "Validating backend development Dockerfile..."
        docker build -f Dockerfile.dev -t cx-futurist-api:dev . --target development
        print_success "Backend development Dockerfile is valid"
    else
        print_warning "Backend development Dockerfile not found"
    fi
    
    if [ -f "frontend/Dockerfile.dev" ]; then
        print_status "Validating frontend development Dockerfile..."
        docker build -f frontend/Dockerfile.dev -t cx-futurist-frontend:dev frontend/ --target development
        print_success "Frontend development Dockerfile is valid"
    else
        print_warning "Frontend development Dockerfile not found"
    fi
}

# Test docker-compose configuration
test_compose() {
    print_status "Validating docker-compose configuration..."
    
    if [ -f "docker-compose.yml" ]; then
        # Validate compose file syntax
        docker-compose config >/dev/null
        print_success "docker-compose.yml syntax is valid"
        
        # Test if services can be created (dry run)
        docker-compose up --no-start
        print_success "docker-compose services can be created"
        
        # Clean up
        docker-compose down --remove-orphans
    else
        print_error "docker-compose.yml not found"
        return 1
    fi
}

# Check for required files
check_required_files() {
    print_status "Checking required files..."
    
    local required_files=(
        "requirements.txt"
        "frontend/package.json"
        ".dockerignore"
        "frontend/.dockerignore"
        ".gcloudignore"
        "cloudbuild.yaml"
        "deploy.sh"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "Found: $file"
        else
            print_warning "Missing: $file"
        fi
    done
}

# Test image sizes
check_image_sizes() {
    print_status "Checking Docker image sizes..."
    
    # Get image sizes
    backend_size=$(docker images cx-futurist-api:test --format "{{.Size}}" | head -1)
    frontend_size=$(docker images cx-futurist-frontend:test --format "{{.Size}}" | head -1)
    
    if [ -n "$backend_size" ]; then
        print_success "Backend image size: $backend_size"
    fi
    
    if [ -n "$frontend_size" ]; then
        print_success "Frontend image size: $frontend_size"
    fi
    
    # Check for reasonable sizes (this is subjective)
    echo ""
    print_status "Image size recommendations:"
    echo "- Backend should be < 1GB for good performance"
    echo "- Frontend should be < 500MB for good performance"
    echo "- Use multi-stage builds to minimize size"
}

# Security check
security_check() {
    print_status "Running basic security checks..."
    
    # Check for secrets in Dockerfiles
    if grep -r "API_KEY\|SECRET\|PASSWORD" Dockerfile* 2>/dev/null; then
        print_error "Found potential secrets in Dockerfiles"
        print_warning "Secrets should be passed via environment variables or Secret Manager"
    else
        print_success "No hardcoded secrets found in Dockerfiles"
    fi
    
    # Check for non-root user
    if grep -q "USER " Dockerfile 2>/dev/null; then
        print_success "Backend Dockerfile uses non-root user"
    else
        print_warning "Backend Dockerfile should specify non-root user"
    fi
    
    if grep -q "USER " frontend/Dockerfile 2>/dev/null; then
        print_success "Frontend Dockerfile uses non-root user"
    else
        print_warning "Frontend Dockerfile should specify non-root user"
    fi
}

# Clean up test images
cleanup() {
    print_status "Cleaning up test images..."
    
    docker rmi cx-futurist-api:test 2>/dev/null || true
    docker rmi cx-futurist-frontend:test 2>/dev/null || true
    docker rmi cx-futurist-api:dev 2>/dev/null || true
    docker rmi cx-futurist-frontend:dev 2>/dev/null || true
    
    # Clean up dangling images
    docker image prune -f >/dev/null 2>&1 || true
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo -e "${GREEN}🐳 Docker Configuration Validation${NC}"
    echo "===================================="
    echo ""
    
    check_docker
    check_required_files
    validate_dockerfiles
    test_compose
    check_image_sizes
    security_check
    
    echo ""
    print_success "Docker validation completed successfully!"
    
    echo ""
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo "1. Run 'docker-compose up' to test locally"
    echo "2. Run './deploy.sh' to deploy to Google Cloud"
    echo "3. Monitor image sizes and optimize if needed"
    
    # Ask if user wants to clean up
    echo ""
    read -p "Clean up test images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup
    fi
}

# Handle script interruption
trap 'print_error "Validation interrupted"; cleanup; exit 1' INT TERM

# Run main function
main "$@"