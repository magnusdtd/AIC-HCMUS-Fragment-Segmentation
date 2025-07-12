#!/bin/bash

# Helm Chart Validation Script
# This script validates the Helm chart syntax and renders templates

set -e

CHART_DIR="$(dirname "$0")"
CHART_NAME="aic-hcmus-fragment-segmentation"

echo "🔍 Validating Helm chart: $CHART_NAME"
echo "======================================"

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install Helm first."
    exit 1
fi

# Validate chart syntax
echo "📋 Validating chart syntax..."
helm lint "$CHART_DIR"

if [ $? -eq 0 ]; then
    echo "✅ Chart syntax is valid"
else
    echo "❌ Chart syntax validation failed"
    exit 1
fi

# Test template rendering with production values
echo "🔧 Testing template rendering with production values..."
helm template "$CHART_NAME" "$CHART_DIR" -f "$CHART_DIR/values.yaml" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Template rendering with production values successful"
else
    echo "❌ Template rendering with production values failed"
    exit 1
fi

# Check for required files
echo "📁 Checking required files..."
required_files=(
    "Chart.yaml"
    "values.yaml"
    "templates/_helpers.tpl"
    "templates/namespace.yaml"
    "templates/secret.yaml"
    "templates/configmap.yaml"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$CHART_DIR/$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
        exit 1
    fi
done

echo ""
echo "🎉 All validations passed! The Helm chart is ready for deployment."
echo ""