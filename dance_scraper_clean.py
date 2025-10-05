# Dance Worlds Scraper - Enhanced Data Extraction with 2025 Rankings
# Handles different website structures and extracts data from multiple sources
# Includes 2025 rankings from https://thedanceworlds.net/rankings/

import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import json

def scrape_dance_worlds_enhanced():
    """
    Enhanced scraper with better data extraction methods and 2025 rankings
    """
    
    print("Dance Worlds Web Scraper Starting")
    print("-" * 60)
    
    # URLs to try - includes the 2025 rankings page
    urls_to_try = [
        "https://thedanceworlds.net/dance-worlds/",
        "https://www.flocheer.com/articles/14115228-dance-worlds-2025-results-here-are-all-the-dance-scores",
        "https://thedanceworlds.net/rankings/"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    all_records = []
    
    for i, url in enumerate(urls_to_try):
        print(f"\nTrying URL {i+1}: {url}")
        
        try:
            print("Sending request...")
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"Success. Got {len(response.text):,} characters")
                
                # Use different extraction method for 2025 rankings
                if "rankings" in url:
                    records = extract_2025_rankings(response.text, url)
                else:
                    records = extract_data_enhanced(response.text, url)
                
                if records:
                    print(f"Found {len(records)} records from this URL")
                    all_records.extend(records)
                else:
                    print("No structured data found")
                    debug_content(response.text, url)
                    
            else:
                print(f"HTTP Error {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        if i < len(urls_to_try) - 1:
            time.sleep(2)
    
    if all_records:
        print(f"\nTotal records found: {len(all_records)}")
        df = create_enhanced_csv(all_records)
        return df
    else:
        print("\nNo structured data found from any URL")
        print("Switching to manual data input method...")
        return try_manual_input()

def extract_2025_rankings(html_content, url):
    """
    Extract 2025 rankings data from thedanceworlds.net/rankings/
    """
    print("Extracting 2025 rankings data...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    records = []
    
    # Find all tables with ranking data
    tables = soup.find_all('table')
    print(f"   Found {len(tables)} tables on 2025 rankings page")
    
    # Track current category being processed
    current_category = "Unknown"
    current_round = "Unknown"
    
    # Look for headers that indicate category and round
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'div']):
        text = element.get_text(strip=True).upper()
        
        # Detect competition round
        if 'FINALS' in text and 'SEMI' not in text:
            current_round = 'Finals'
        elif 'SEMI-FINALS' in text:
            current_round = 'Semi-Finals'
        elif 'PRELIMS' in text:
            current_round = 'Prelims'
        
        # Detect dance categories
        if any(category in text for category in ['KICK', 'CONTEMPORARY', 'LYRICAL', 'JAZZ', 'POM', 'HIP HOP', 'COED']):
            # Extract category details
            if 'SENIOR KICK' in text:
                current_category = 'Senior Kick'
            elif 'SENIOR SMALL CONTEMPORARY' in text or 'SENIOR SMALL LYRICAL' in text:
                current_category = 'Senior Small Contemporary/Lyrical'
            elif 'SENIOR LARGE CONTEMPORARY' in text or 'SENIOR LARGE LYRICAL' in text:
                current_category = 'Senior Large Contemporary/Lyrical'
            elif 'SENIOR SMALL JAZZ' in text:
                current_category = 'Senior Small Jazz'
            elif 'SENIOR LARGE JAZZ' in text:
                current_category = 'Senior Large Jazz'
            elif 'SENIOR SMALL POM' in text:
                current_category = 'Senior Small Pom'
            elif 'SENIOR LARGE POM' in text:
                current_category = 'Senior Large Pom'
            elif 'SENIOR SMALL HIP HOP' in text:
                current_category = 'Senior Small Hip Hop'
            elif 'SENIOR LARGE HIP HOP' in text:
                current_category = 'Senior Large Hip Hop'
            elif 'SENIOR SMALL COED HIP HOP' in text:
                current_category = 'Senior Small Coed Hip Hop'
            elif 'SENIOR LARGE COED HIP HOP' in text:
                current_category = 'Senior Large Coed Hip Hop'
            elif 'OPEN' in text and 'LYRICAL' in text:
                current_category = 'Open Contemporary/Lyrical'
            elif 'OPEN' in text and 'JAZZ' in text and 'COED' not in text:
                current_category = 'Open Jazz'
            elif 'OPEN' in text and 'JAZZ' in text and 'COED' in text:
                current_category = 'Open Coed Jazz'
            elif 'OPEN' in text and 'POM' in text and 'COED' not in text:
                current_category = 'Open Pom'
            elif 'OPEN' in text and 'POM' in text and 'COED' in text:
                current_category = 'Open Coed Pom'
            elif 'OPEN' in text and 'HIP HOP' in text and 'COED' not in text:
                current_category = 'Open Hip Hop'
            elif 'OPEN' in text and 'HIP HOP' in text and 'COED' in text:
                current_category = 'Open Coed Hip Hop'
            elif 'JUNIOR' in text:
                current_category = 'Junior Dance'
    
    # Process each table
    for table in tables:
        rows = table.find_all('tr')
        
        # Skip if no rows
        if not rows:
            continue
            
        # Check if this is a ranking table by looking for ranking headers
        header_row = rows[0] if rows else None
        if header_row:
            header_text = header_row.get_text().upper()
            if not any(word in header_text for word in ['RANKING', 'RANK', 'CLUB', 'TEAM']):
                continue
        
        # Process data rows (skip header)
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                continue
                
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            try:
                # Extract ranking (first column)
                rank_text = cell_texts[0]
                rank_match = re.search(r'(\d+)', rank_text)
                if not rank_match:
                    continue
                rank = int(rank_match.group(1))
                
                # Extract club/studio (second column)
                club = cell_texts[1] if len(cell_texts) > 1 else ""
                
                # Extract team name (third column)
                team = cell_texts[2] if len(cell_texts) > 2 else ""
                
                # Extract scores if available
                raw_score = ""
                event_score = ""
                if len(cell_texts) > 3:
                    for i, cell in enumerate(cell_texts[3:], 3):
                        if re.match(r'^\d+\.?\d*$', cell):
                            if not raw_score:
                                raw_score = cell
                            elif not event_score:
                                event_score = cell
                
                # Determine country from team name or context
                country = extract_country_from_text(f"{club} {team}")
                
                # Create record
                record = {
                    'Year': 2025,
                    'Rank': rank,
                    'Category': current_category,
                    'Studio_Name': club,
                    'Team_Name': team,
                    'Country': country,
                    'Round': current_round,
                    'Raw_Score': raw_score,
                    'Event_Score': event_score,
                    'Source': '2025_Rankings_Table'
                }
                
                records.append(record)
                
            except (ValueError, IndexError) as e:
                continue
    
    print(f"   Extracted {len(records)} records from 2025 rankings")
    return records

def extract_country_from_text(text):
    """
    Extract country from text using country codes and names
    """
    text_upper = text.upper()
    
    # Country codes mapping
    country_codes = {
        'USA': 'USA', 'US': 'USA',
        'JPN': 'Japan', 'JAPAN': 'Japan',
        'AUS': 'Australia', 'AUSTRALIA': 'Australia',
        'ENG': 'England', 'ENGLAND': 'England',
        'SCT': 'Scotland', 'SCOTLAND': 'Scotland',
        'WLS': 'Wales', 'WALES': 'Wales',
        'CAN': 'Canada', 'CANADA': 'Canada',
        'MEX': 'Mexico', 'MEXICO': 'Mexico',
        'ECU': 'Ecuador', 'ECUADOR': 'Ecuador',
        'CHL': 'Chile', 'CHILE': 'Chile',
        'COL': 'Colombia', 'COLOMBIA': 'Colombia',
        'FRA': 'France', 'FRANCE': 'France',
        'GER': 'Germany', 'GERMANY': 'Germany',
        'NLD': 'Netherlands', 'NETHERLANDS': 'Netherlands',
        'SWE': 'Sweden', 'SWEDEN': 'Sweden',
        'UKR': 'Ukraine', 'UKRAINE': 'Ukraine',
        'TPE': 'Taiwan', 'TAIWAN': 'Taiwan',
        'MCO': 'Monaco', 'MONACO': 'Monaco'
    }
    
    # Look for country codes in parentheses
    paren_match = re.search(r'\(([A-Z]{2,4})\)', text_upper)
    if paren_match:
        code = paren_match.group(1)
        return country_codes.get(code, code)
    
    # Look for country names or codes directly
    for code, country in country_codes.items():
        if code in text_upper or country.upper() in text_upper:
            return country
    
    return 'Unknown'

def extract_data_enhanced(html_content, url):
    """
    Enhanced data extraction with multiple methods
    """
    
    print("Analyzing content with enhanced methods...")
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    records = []
    
    # Method 1: Look for tables with competition data
    print("Method 1: Looking for HTML tables...")
    records.extend(extract_from_tables(soup))
    
    # Method 2: Look for structured lists
    print("Method 2: Looking for structured lists...")
    records.extend(extract_from_lists(soup))
    
    # Method 3: Look for JSON data embedded in the page
    print("Method 3: Looking for embedded JSON data...")
    records.extend(extract_from_json(html_content))
    
    # Method 4: Advanced text pattern matching
    print("Method 4: Advanced text pattern matching...")
    records.extend(extract_from_text_advanced(soup.get_text()))
    
    # Method 5: Look for specific dance-related elements
    print("Method 5: Looking for dance-specific elements...")
    records.extend(extract_dance_specific(soup))
    
    # Remove duplicates
    unique_records = remove_duplicates(records)
    
    return unique_records

def extract_from_tables(soup):
    """Extract data from HTML tables"""
    records = []
    
    tables = soup.find_all('table')
    print(f"   Found {len(tables)} tables")
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Look for rows that might contain competition data
            if len(cell_texts) >= 4:
                # Check if first cell looks like a year
                if cell_texts[0].isdigit() and len(cell_texts[0]) == 4:
                    year = int(cell_texts[0])
                    if 2015 <= year <= 2025:
                        # Check if second cell looks like a rank
                        rank_match = re.search(r'(\d+)', cell_texts[1])
                        if rank_match:
                            rank = int(rank_match.group(1))
                            if 1 <= rank <= 100:
                                records.append({
                                    'Year': year,
                                    'Rank': rank,
                                    'Category': cell_texts[2] if len(cell_texts) > 2 else "",
                                    'Studio_Name': cell_texts[3] if len(cell_texts) > 3 else "",
                                    'Team_Name': cell_texts[4] if len(cell_texts) > 4 else "",
                                    'Country': extract_country_from_text(cell_texts[3] if len(cell_texts) > 3 else ""),
                                    'Source': 'HTML_Table'
                                })
    
    return records

def extract_from_lists(soup):
    """Extract data from HTML lists"""
    records = []
    
    # Look for ordered and unordered lists
    lists = soup.find_all(['ul', 'ol'])
    print(f"   Found {len(lists)} lists")
    
    for list_element in lists:
        items = list_element.find_all('li')
        
        for item in items:
            text = item.get_text(strip=True)
            
            # Look for competition data patterns in list items
            patterns = [
                r'(\d{4})\s*[-|]\s*(\d+)\s*[-|]\s*([^-|]+)[-|]\s*([^-|]+)',
                r'(\d{4})\s+(\d+)\s+([A-Za-z][^\d\n]{5,40})\s+([A-Za-z][^\d\n]{5,40})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        year = int(match.group(1))
                        rank = int(match.group(2))
                        
                        if 2015 <= year <= 2025 and 1 <= rank <= 100:
                            records.append({
                                'Year': year,
                                'Rank': rank,
                                'Category': match.group(3).strip(),
                                'Studio_Name': match.group(4).strip(),
                                'Team_Name': "",
                                'Country': extract_country_from_text(match.group(4).strip()),
                                'Source': 'HTML_List'
                            })
                    except ValueError:
                        continue
    
    return records

def extract_from_json(html_content):
    """Look for JSON data embedded in the HTML"""
    records = []
    
    # Look for JSON in script tags
    json_patterns = [
        r'<script[^>]*>(.*?)</script>',
        r'var\s+data\s*=\s*(\{.*?\});',
        r'window\.\w+\s*=\s*(\[.*?\]);',
        r'"results"\s*:\s*(\[.*?\])',
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        for match in matches:
            try:
                # Try to find JSON-like structures
                json_candidates = re.findall(r'\{[^{}]*"year"[^{}]*\}', match)
                json_candidates.extend(re.findall(r'\{[^{}]*"rank"[^{}]*\}', match))
                json_candidates.extend(re.findall(r'\{[^{}]*\d{4}[^{}]*\}', match))
                
                for candidate in json_candidates:
                    try:
                        data = json.loads(candidate)
                        if isinstance(data, dict) and 'year' in data:
                            records.append({
                                'Year': data.get('year'),
                                'Rank': data.get('rank', data.get('position', 999)),
                                'Category': data.get('category', data.get('division', '')),
                                'Studio_Name': data.get('studio', data.get('team', '')),
                                'Team_Name': data.get('name', ''),
                                'Country': extract_country_from_text(data.get('studio', data.get('team', ''))),
                                'Source': 'Embedded_JSON'
                            })
                    except json.JSONDecodeError:
                        continue
                        
            except Exception:
                continue
    
    return records

def extract_from_text_advanced(text):
    """Advanced text pattern matching"""
    records = []
    
    # More sophisticated patterns
    advanced_patterns = [
        # Pattern for "2024 1st Place Junior Dance WINGFLAP"
        r'(\d{4})\s+(\d+)(?:st|nd|rd|th)?\s+Place\s+([^0-9\n]{5,50})\s+([A-Za-z][^\n]{5,50})',
        
        # Pattern for "Year: 2024, Rank: 1, Category: Junior Dance, Studio: WINGFLAP"
        r'Year:\s*(\d{4}).*?Rank:\s*(\d+).*?Category:\s*([^,\n]+).*?Studio:\s*([^,\n]+)',
        
        # Pattern for numbered results like "1. WINGFLAP - Junior Dance - 2024"
        r'(\d+)\.\s+([A-Za-z][^-\n]{5,40})\s*-\s*([^-\n]{5,40})\s*-\s*(\d{4})',
        
        # Pattern for tab or multiple space separated data
        r'(\d{4})\s{2,}(\d+)\s{2,}([^\t\n]{5,40})\s{2,}([^\t\n]{5,40})',
        
        # Pattern for competition results with country codes
        r'(\d{4})\s*[\|,]\s*(\d+)\s*[\|,]\s*([^|\n,]{5,50})\s*[\|,]\s*([^|\n,]{5,50})\s*\([A-Z]{2,4}\)',
        
        # Very flexible pattern for any year followed by reasonable text
        r'(\d{4})\D{1,20}(\d{1,2})\D{1,50}([A-Za-z][^0-9\n]{10,60}?)\s+([A-Za-z][^0-9\n]{5,50})',
    ]
    
    for i, pattern in enumerate(advanced_patterns):
        matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
        
        if matches:
            print(f"   Pattern {i+1} found {len(matches)} matches")
            
            for match in matches:
                try:
                    # Different patterns have different group orders
                    if i == 2:
                        year = int(match[3])
                        rank = int(match[0])
                        category = match[2].strip()
                        studio = match[1].strip()
                    else:
                        year = int(match[0])
                        rank = int(match[1])
                        category = match[2].strip() if len(match) > 2 else ""
                        studio = match[3].strip() if len(match) > 3 else ""
                    
                    if 2015 <= year <= 2025 and 1 <= rank <= 100:
                        records.append({
                            'Year': year,
                            'Rank': rank,
                            'Category': category,
                            'Studio_Name': studio,
                            'Team_Name': "",
                            'Country': extract_country_from_text(studio),
                            'Source': f'Advanced_Pattern_{i+1}'
                        })
                        
                except (ValueError, IndexError):
                    continue
    
    return records

def extract_dance_specific(soup):
    """Look for dance-specific HTML elements and classes"""
    records = []
    
    # Look for elements with dance-related class names or IDs
    dance_selectors = [
        '[class*="result"]', '[class*="ranking"]', '[class*="competition"]',
        '[class*="dance"]', '[class*="team"]', '[class*="studio"]',
        '[id*="result"]', '[id*="ranking"]', '[id*="competition"]',
        '.results', '.rankings', '.teams', '.studios'
    ]
    
    for selector in dance_selectors:
        try:
            elements = soup.select(selector)
            
            for element in elements:
                text = element.get_text(strip=True)
                
                # Look for year and rank patterns in these elements
                year_match = re.search(r'20(1[5-9]|2[0-5])', text)
                rank_match = re.search(r'\b([1-9]|[1-9][0-9]|100)\b', text)
                
                if year_match and rank_match:
                    # Found potential competition data
                    year = int(year_match.group(0))
                    rank = int(rank_match.group(1))
                    
                    # Extract other information
                    text_parts = re.split(r'[|\-,\n\t]', text)
                    text_parts = [part.strip() for part in text_parts if len(part.strip()) > 2]
                    
                    category = ""
                    studio = ""
                    
                    # Try to identify category and studio from the text parts
                    for part in text_parts:
                        if any(dance_term in part.lower() for dance_term in ['dance', 'hip hop', 'jazz', 'pom', 'contemporary']):
                            if not category:
                                category = part
                        elif len(part) > 3 and part not in [str(year), str(rank)]:
                            if not studio:
                                studio = part
                    
                    if category or studio:
                        records.append({
                            'Year': year,
                            'Rank': rank,
                            'Category': category,
                            'Studio_Name': studio,
                            'Team_Name': "",
                            'Country': extract_country_from_text(studio),
                            'Source': 'Dance_Specific_Elements'
                        })
                        
        except Exception:
            continue
    
    return records

def remove_duplicates(records):
    """Remove duplicate records"""
    seen = set()
    unique_records = []
    
    for record in records:
        # Create a key for deduplication
        key = (record.get('Year'), record.get('Rank'), 
               record.get('Category', '').lower(), record.get('Studio_Name', '').lower())
        
        if key not in seen and record.get('Year') and record.get('Rank'):
            seen.add(key)
            unique_records.append(record)
    
    return unique_records

def debug_content(html_content, url):
    """Debug what content we actually found"""
    print("\nDebugging content analysis")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    
    # Look for dance-related keywords
    dance_keywords = ['dance', 'worlds', 'competition', 'hip hop', 'jazz', 'pom', 'contemporary', 'studio', 'team']
    found_keywords = []
    
    for keyword in dance_keywords:
        count = text.lower().count(keyword.lower())
        if count > 0:
            found_keywords.append(f"{keyword}: {count}")
    
    print(f"Dance keywords found: {', '.join(found_keywords[:5])}")
    
    # Look for year patterns
    years = re.findall(r'20(1[5-9]|2[0-5])', text)
    unique_years = sorted(set(years))
    if unique_years:
        print(f"Years found: {', '.join(['20' + y for y in unique_years])}")
    
    # Look for number patterns that could be ranks
    ranks = re.findall(r'\b([1-9]|[1-4][0-9]|50)\b', text)
    if ranks:
        print(f"Potential ranks found: {len(set(ranks))} unique numbers")
    
    # Show sample of content
    print(f"\nContent sample (first 500 chars):")
    sample_text = re.sub(r'\s+', ' ', text[:500])
    print(f"   {sample_text}...")
    
    # Look for specific patterns we might have missed
    potential_data_lines = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if len(line) > 20:
            # Look for lines with years and numbers
            if re.search(r'20(1[5-9]|2[0-5])', line) and re.search(r'\b[1-9]\b', line):
                potential_data_lines.append(line)
    
    if potential_data_lines:
        print(f"\nFound {len(potential_data_lines)} lines with years and numbers:")
        for i, line in enumerate(potential_data_lines[:3]):
            print(f"   {i+1}: {line[:100]}...")

def try_manual_input():
    """Fallback to manual data input"""
    print("\nAlternative: Manual data input")
    print("Since automatic extraction did not work, manual input is available")
    print()
    print("Please go to: https://thedanceworlds.net/dance-worlds/")
    print("Copy the competition results data")
    print("Paste it below (press Enter twice when done)")
    print()
    
    try:
        response = input("Would you like to try manual input? (y/n): ").lower()
        
        if response == 'y':
            print("\nPaste your data below (press Enter on empty line to finish):")
            print("-" * 50)
            
            lines = []
            while True:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
            
            if lines:
                raw_data = '\n'.join(lines)
                print(f"\nReceived {len(lines)} lines of data")
                
                # Process the manually entered data
                records = extract_from_text_advanced(raw_data)
                
                if records:
                    print(f"Extracted {len(records)} records from your input")
                    df = create_enhanced_csv(records)
                    return df
                else:
                    print("Could not extract structured data from input")
                    return None
            else:
                print("No data entered")
                return None
        else:
            print("Manual input skipped")
            return None
            
    except KeyboardInterrupt:
        print("\nInput cancelled")
        return None

def create_enhanced_csv(records):
    """Create enhanced CSV with additional processing"""
    print(f"\nProcessing {len(records)} records...")
    
    # Clean and enhance the records
    enhanced_records = []
    
    for record in records:
        # Extract country from team info if not already set
        country = record.get('Country', 'Unknown')
        if country == 'Unknown':
            team_info = f"{record.get('Team_Name', '')} {record.get('Studio_Name', '')}"
            country = extract_country_from_text(team_info)
        
        # Clean team name
        team_name = record.get('Team_Name', '')
        if not team_name:
            team_name = record.get('Studio_Name', '')
        
        # Remove country codes from team names
        team_name = re.sub(r'\([^)]+\)', '', team_name).strip()
        
        # Categorize dance type
        category = record.get('Category', '')
        dance_type = categorize_dance_type(category)
        
        enhanced_record = {
            'Year': record.get('Year'),
            'Rank': record.get('Rank'),
            'Category': category,
            'Studio_Name': record.get('Studio_Name', ''),
            'Team_Name': team_name,
            'Country': country,
            'Dance_Type': dance_type,
            'Round': record.get('Round', 'Final'),
            'Raw_Score': record.get('Raw_Score', ''),
            'Event_Score': record.get('Event_Score', ''),
            'Is_Champion': 1 if record.get('Rank') == 1 else 0,
            'Is_Podium': 1 if record.get('Rank', 999) <= 3 else 0,
            'Data_Source': record.get('Source', 'Unknown')
        }
        
        enhanced_records.append(enhanced_record)
    
    # Create DataFrame
    df = pd.DataFrame(enhanced_records)
    
    # Sort by year, category, and rank
    df = df.sort_values(['Year', 'Category', 'Rank']).reset_index(drop=True)
    
    # Filter to only keep Final round records
    df = df[df['Round'] == 'Final'].reset_index(drop=True)
    
    # Remove columns not needed in final dataset
    columns_to_drop = ['Round', 'Raw_Score', 'Event_Score', 'Is_Champion', 'Is_Podium', 'Data_Source']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'dance_worlds_data_{timestamp}.csv'
    
    # Save to CSV
    df.to_csv(filename, index=False)
    
    print(f"Enhanced CSV saved as: {filename}")
    
    # Show detailed summary
    print_enhanced_summary(df)
    
    return df

def categorize_dance_type(category):
    """Categorize dance types"""
    if not category:
        return "Unknown"
    
    category_lower = category.lower()
    
    if 'hip hop' in category_lower:
        return 'Hip Hop'
    elif 'jazz' in category_lower:
        return 'Jazz'
    elif 'pom' in category_lower:
        return 'Pom'
    elif 'contemporary' in category_lower or 'lyrical' in category_lower:
        return 'Contemporary/Lyrical'
    elif 'kick' in category_lower:
        return 'Kick'
    elif 'junior' in category_lower and 'dance' in category_lower:
        return 'Junior Dance'
    else:
        return 'Other'

def print_enhanced_summary(df):
    """Print detailed summary of the data"""
    print(f"\nEnhanced data summary:")
    print(f"   Total Records: {len(df)}")
    
    if len(df) > 0:
        print(f"   Years Covered: {df['Year'].min()} - {df['Year'].max()}")
        print(f"   Countries: {df['Country'].nunique()}")
        print(f"   Dance Types: {df['Dance_Type'].nunique()}")
        print(f"   Studios: {df['Studio_Name'].nunique()}")
        
        print(f"\nData by Year:")
        year_counts = df['Year'].value_counts().sort_index()
        for year, count in year_counts.items():
            print(f"   {year}: {count} records")
        
        print(f"\nDance Types Found:")
        dance_types = df['Dance_Type'].value_counts()
        for dance_type, count in dance_types.items():
            print(f"   {dance_type}: {count}")
        
        print(f"\nTop Countries:")
        countries = df['Country'].value_counts().head(10)
        for country, count in countries.items():
            print(f"   {country}: {count}")
        
        print(f"\nSample Data:")
        sample_cols = ['Year', 'Rank', 'Category', 'Studio_Name', 'Country']
        print(df[sample_cols].head(10).to_string(index=False))
        
        if 2025 in df['Year'].values:
            print(f"\n2025 Champions (Rank 1):")
            champions_2025 = df[(df['Year'] == 2025) & (df['Rank'] == 1)]
            if len(champions_2025) > 0:
                for _, champion in champions_2025.iterrows():
                    print(f"   {champion['Category']}: {champion['Studio_Name']} - {champion['Team_Name']} ({champion['Country']})")

if __name__ == "__main__":
    print("Dance Worlds Scraper with 2025 Rankings")
    print("This version uses multiple extraction methods and includes 2025 rankings")
    
    try:
        result_df = scrape_dance_worlds_enhanced()
        
        if result_df is not None and len(result_df) > 0:
            print("\nScraping completed successfully")
        else:
            print("\nScraping completed but no data extracted")
            print("The websites may have changed structure")
            print("Try the manual input method shown above")
            
    except KeyboardInterrupt:
        print("\nScraping cancelled by user")
    
    input("\nPress Enter to close...")