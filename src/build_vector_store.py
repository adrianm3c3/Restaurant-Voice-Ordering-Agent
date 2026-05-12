from src.knowledge_builder import build_knowledge_chunks
from src.knowledge_builder import load_menu
from src.retriever_chroma import build_chroma_collection


def main():
    menu = load_menu()

    chunks = build_knowledge_chunks(menu)

    build_chroma_collection(chunks)

    print("Chroma vector store built.")


if __name__ == "__main__":
    main()