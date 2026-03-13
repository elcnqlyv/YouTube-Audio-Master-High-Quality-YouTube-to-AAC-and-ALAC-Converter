import FreeSimpleGUI as sg
import os
import threading
import subprocess
import platform
from pathlib import Path
from datetime import datetime
import yt_dlp
import shutil

# Configure FreeSimpleGUI theme
sg.theme('DarkBlue3')
sg.set_options(font=('Arial', 10))

class YouTubeAudioConverter:
    def __init__(self):
        self.download_folder = str(Path.home() / "Downloads")
        self.is_converting = False
        self.output_format = 'aac'
        self.quality = '192'
        
    def log_message(self, message, window=None):
        """Add a timestamped message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        if window:
            window['-LOG-'].print(log_entry)
        return log_entry
    
    def validate_url(self, url):
        """Validate if the URL is a valid YouTube URL"""
        return 'youtube.com' in url or 'youtu.be' in url
    
    def handle_file_conflict(self, filepath):
        """Handle case where file already exists"""
        if os.path.exists(filepath):
            layout = [
                [sg.Text(f"File already exists:\n{os.path.basename(filepath)}", size=(50, 3))],
                [sg.Button('Overwrite'), sg.Button('Rename'), sg.Button('Cancel')]
            ]
            window = sg.Window('File Conflict', layout)
            event, _ = window.read()
            window.close()
            
            if event == 'Overwrite':
                os.remove(filepath)
                return filepath
            elif event == 'Rename':
                name, ext = os.path.splitext(filepath)
                counter = 1
                new_filepath = f"{name}_{counter}{ext}"
                while os.path.exists(new_filepath):
                    counter += 1
                    new_filepath = f"{name}_{counter}{ext}"
                return new_filepath
            else:
                return None
        return filepath
    
    def download_and_convert(self, url, output_format, quality, window):
        """Download YouTube audio and convert to desired format"""
        try:
            self.is_converting = True
            self.log_message(f"Starting download from: {url}", window)
            
            # Validate URL
            if not self.validate_url(url):
                self.log_message("❌ Invalid YouTube URL", window)
                self.is_converting = False
                return False
            
            # Prepare output template
            output_template = os.path.join(self.download_folder, '%(title)s')
            
            # Download audio using yt-dlp
            self.log_message("📥 Downloading audio from YouTube...", window)
            
            # Map output format to codec
            codec_map = {
                'aac': 'aac',
                'alac': 'alac',
                'mp3': 'mp3'
            }
            
            codec = codec_map.get(output_format.lower(), 'aac')
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': codec,
                    'preferredquality': quality,
                    'nopostoverwrites': False,
                }],
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [lambda d: self.progress_hook(d, window)]
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log_message("🔍 Extracting video information...", window)
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'audio')
                
                # Determine file extension
                ext_map = {
                    'aac': 'm4a',
                    'alac': 'm4a',
                    'mp3': 'mp3'
                }
                ext = ext_map.get(output_format.lower(), 'm4a')
                
                final_file = os.path.join(self.download_folder, f"{video_title}.{ext}")
            
            # Handle file conflicts
            final_file = self.handle_file_conflict(final_file)
            
            if final_file:
                self.log_message(f"✅ Download and conversion complete!", window)
                self.log_message(f"📁 Saved to: {final_file}", window)
                self.is_converting = False
                return True
            else:
                self.log_message("⚠️  Operation cancelled by user", window)
                self.is_converting = False
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}", window)
            import traceback
            self.log_message(f"Details: {traceback.format_exc()}", window)
            self.is_converting = False
            return False
    
    def progress_hook(self, d, window):
        """Handle download progress updates"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', '0s')
            self.log_message(f"Progress: {percent} | Speed: {speed} | ETA: {eta}", window)
        elif d['status'] == 'finished':
            self.log_message("📦 Download finished, now converting...", window)
        elif d['status'] == 'error':
            self.log_message(f"❌ Error during download: {d.get('error', 'Unknown error')}", window)

def create_window():
    """Create the main window layout"""
    layout = [
        [sg.Text('🎵 YouTube Audio Master - Desktop Edition', font=('Arial', 14, 'bold'))],
        [sg.Text('Convert YouTube videos to high-quality AAC and ALAC audio', font=('Arial', 9))],
        [sg.Text('_' * 70)],
        
        # URL Input
        [sg.Text('YouTube URL:', size=(15, 1), font=('Arial', 10)), 
         sg.InputText(key='-URL-', size=(45, 1), focus=True, tooltip='Paste YouTube video or playlist URL')],
        
        # Format and Quality Row
        [sg.Text('Output Format:', size=(15, 1), font=('Arial', 10)),
         sg.Combo(['AAC', 'ALAC', 'MP3'], default_value='AAC', key='-FORMAT-', size=(12, 1), readonly=True),
         sg.Text('Quality (kbps):', font=('Arial', 10)),
         sg.Combo(['128', '192', '256', '320'], default_value='192', key='-QUALITY-', size=(12, 1), readonly=True)],
        
        # Download Folder
        [sg.Text('Download Folder:', size=(15, 1), font=('Arial', 10)), 
         sg.InputText(key='-FOLDER-', size=(35, 1), disabled=True),
         sg.FolderBrowse(button_text='Browse', key='-BROWSE-', size=(10, 1))],
        
        [sg.Text('_' * 70)],
        
        # Buttons
        [sg.Button('Convert & Download', size=(20, 1), button_color=('white', 'green'), font=('Arial', 10, 'bold')),
         sg.Button('Clear Log', size=(15, 1), font=('Arial', 10)),
         sg.Button('Open Folder', size=(15, 1), font=('Arial', 10)),
         sg.Button('Exit', size=(10, 1), font=('Arial', 10))],
        
        [sg.Text('_' * 70)],
        
        # Progress Bar
        [sg.ProgressBar(100, orientation='h', size=(65, 20), key='-PROGRESS-', bar_color=('green', 'lightgray'))],
        
        # Status Text
        [sg.Text('Status: Ready', key='-STATUS-', size=(70, 1), font=('Arial', 9))],
        
        # Log Output
        [sg.Multiline(size=(80, 18), key='-LOG-', disabled=True, 
              autoscroll=True, background_color='#1a1a1a', text_color='#00FF00',
              font=('Courier', 9))],
    ]
    
    return sg.Window('YouTube Audio Master', layout, finalize=True, size=(850, 750), resizable=True)

def main():
    converter = YouTubeAudioConverter()
    window = create_window()
    
    # Initialize log
    converter.log_message("🚀 YouTube Audio Master started successfully", window)
    converter.log_message("Enter a YouTube URL and click 'Convert & Download' to begin", window)
    converter.log_message("Supported: Videos, Playlists, Shorts", window)
    window['-FOLDER-'].update(converter.download_folder)
    
    while True:
        event, values = window.read(timeout=100)
        
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            converter.log_message("👋 Closing application...", window)
            break
        
        elif event == 'Browse':
            folder = sg.popup_get_folder('Select Download Folder', default_path=converter.download_folder)
            if folder:
                converter.download_folder = folder
                window['-FOLDER-'].update(converter.download_folder)
                converter.log_message(f"📁 Download folder changed to: {folder}", window)
        
        elif event == 'Clear Log':
            window['-LOG-'].update('')
            converter.log_message("Log cleared", window)
        
        elif event == 'Open Folder':
            if os.path.exists(converter.download_folder):
                if platform.system() == 'Windows':
                    os.startfile(converter.download_folder)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.Popen(['open', converter.download_folder])
                else:  # Linux
                    subprocess.Popen(['xdg-open', converter.download_folder])
                converter.log_message(f"📂 Opening folder: {converter.download_folder}", window)
            else:
                sg.popup_error(f"Folder not found: {converter.download_folder}")
        
        elif event == 'Convert & Download':
            url = values['-URL-'].strip()
            format_choice = values['-FORMAT-'].lower()
            quality = values['-QUALITY-']
            
            # Validate inputs
            if not url:
                sg.popup_error('Please enter a YouTube URL', title='Input Required')
                continue
            
            converter.download_folder = values['-FOLDER-']
            
            # Disable button during conversion
            window['Convert & Download'].update(disabled=True)
            window['-STATUS-'].update('Status: Converting... (This may take a few minutes)')
            
            # Run in thread to prevent UI freezing
            thread = threading.Thread(
                target=converter.download_and_convert,
                args=(url, format_choice, quality, window),
                daemon=True
            )
            thread.start()
            
            # Update UI while converting
            progress = 0
            while converter.is_converting:
                event, _ = window.read(timeout=200)
                
                if event == sg.WINDOW_CLOSED or event == 'Exit':
                    break
                
                progress = (progress + 10) % 100
                window['-PROGRESS-'].update_bar(progress)
            
            # Conversion complete
            window['Convert & Download'].update(disabled=False)
            window['-PROGRESS-'].update_bar(0)
            window['-STATUS-'].update('Status: Ready')
            converter.log_message("=" * 70, window)
    
    window.close()

if __name__ == '__main__':
    main()