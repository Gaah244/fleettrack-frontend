#!/bin/bash
# Render Frontend Build Script

echo "Installing frontend dependencies..."
yarn install

echo "Building React application..."
yarn build

echo "Build completed successfully!"