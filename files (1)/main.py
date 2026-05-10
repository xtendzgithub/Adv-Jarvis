"""
╔═══════════════════════════════════════════════════════════════╗
║           J.A.R.V.I.S. — GitHub Intelligence System          ║
║      Just A Rather Very Intelligent System v2.0              ║
╚═══════════════════════════════════════════════════════════════╝
"""

import sys
import os

# Ensure jarvis package is importable
sys.path.insert(0, os.path.dirname(__file__))

from jarvis.assistant import JarvisAssistant


def main():
    print("""
    ╔══════════════════════════════════════════╗
    ║   J.A.R.V.I.S.  GitHub Edition v2.0     ║
    ║   Initializing systems...               ║
    ╚══════════════════════════════════════════╝
    """)
    assistant = JarvisAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
