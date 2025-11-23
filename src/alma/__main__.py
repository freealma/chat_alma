#!/usr/bin/env python3
"""
Punto de entrada principal para Alma
"""
import argparse
from alma.core.agent import AlmaAgent

def main():
    parser = argparse.ArgumentParser(description='Alma RAG System')
    parser.add_argument('--embeddings', action='store_true', 
                       help='Generate embeddings for chunks')
    
    args = parser.parse_args()
    
    agent = AlmaAgent()
    
    if args.embeddings:
        agent.generate_embeddings()
    else:
        agent.chat_mode()

if __name__ == "__main__":
    main()