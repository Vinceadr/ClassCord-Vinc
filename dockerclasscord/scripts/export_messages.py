#!/usr/bin/env python3
import sqlite3
import json
import csv
import sys
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path('../data/classcord.db')

def export_to_json(channel=None, output_file=None):
    """Exporte les messages en format JSON"""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        channel_suffix = f"_{channel.replace('#', '')}" if channel else ""
        output_file = f"messages{channel_suffix}_{timestamp}.json"
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if channel:
            cursor.execute(
                "SELECT username, channel, content, timestamp FROM messages WHERE channel = ? ORDER BY timestamp",
                (channel,)
            )
        else:
            cursor.execute(
                "SELECT username, channel, content, timestamp FROM messages ORDER BY channel, timestamp"
            )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'username': row['username'],
                'channel': row['channel'],
                'content': row['content'],
                'timestamp': row['timestamp']
            })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    
    print(f"Exportation JSON terminée: {len(messages)} messages exportés dans {output_file}")
    return output_file

def export_to_csv(channel=None, output_file=None):
    """Exporte les messages en format CSV"""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        channel_suffix = f"_{channel.replace('#', '')}" if channel else ""
        output_file = f"messages{channel_suffix}_{timestamp}.csv"
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        if channel:
            cursor.execute(
                "SELECT username, channel, content, timestamp FROM messages WHERE channel = ? ORDER BY timestamp",
                (channel,)
            )
        else:
            cursor.execute(
                "SELECT username, channel, content, timestamp FROM messages ORDER BY channel, timestamp"
            )
        
        messages = cursor.fetchall()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Username', 'Channel', 'Content', 'Timestamp'])
        writer.writerows(messages)
    
    print(f"Exportation CSV terminée: {len(messages)} messages exportés dans {output_file}")
    return output_file

def list_channels():
    """Liste les canaux disponibles dans la base de données"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT channel FROM messages ORDER BY channel")
        channels = [row[0] for row in cursor.fetchall()]
    
    print("Canaux disponibles:")
    for channel in channels:
        cursor.execute("SELECT COUNT(*) FROM messages WHERE channel = ?", (channel,))
        count = cursor.fetchone()[0]
        print(f"- {channel}: {count} messages")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  export_messages.py json [channel] [output_file]")
        print("  export_messages.py csv [channel] [output_file]")
        print("  export_messages.py list")
        return
    
    if sys.argv[1] == "list":
        list_channels()
        return
    
    format_type = sys.argv[1]
    channel = sys.argv[2] if len(sys.argv) > 2 else None
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    if format_type == "json":
        export_to_json(channel, output_file)
    elif format_type == "csv":
        export_to_csv(channel, output_file)
    else:
        print("Format non supporté. Utilisez 'json' ou 'csv'.")

if __name__ == "__main__":
    main()