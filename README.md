# Dance World Championship Analysis

## Project Overview
This project analyses 11 years of competition data from The Dance Worlds, the world’s largest all star international dance championship. As I competed myself in the competition placing 15th in the Open Contemporary and Lyrical division with Explosion from Intensity Cheer and Dance, England, I wanted to understand the patterns behind this incredible competition. Through web scraping, data cleaning, and interactive visualisations, I have created a comprehensive analysis of 1,953 performances across 40 countries from 2015 to 2025. 

Live Dashboard: https://public.tableau.com/app/profile/nicole.reeves2241/viz/Dance_Worlds/Dashboard1

## Key Findings 
The analysis reveals that 199 world championship titles were awarded across these 11 years, with 40 countries represented and 1,953 total performance. The United States dominated with the highest championship count, followed by Japan and England. Hip hop leads as the most popular style with 646 performances, whilst Contemporary/Lyrical follows with 254 performances. The data shows consistent growth in participation from 205 to 2025, demonstrating the expanding reach of competitive dance globally. 

## Technical Process
### Data Collection
I used Python with Beautiful Soup and Selenium to scrape competition results from The Dance World Official website. The scraping process covered all divisions and categories from 2015 through 2025, extracting team rankings, studio names, countries, dance types, and team classifications. Different years presented varying HTML structures, requiring flexible parsing functions that could adapt. 

### Data Cleaning 
The raw data required significant standardisation work. Country names appeared in multiple formats and needed consistent representation whilst respecting regional distinctions, particularly maintaining England as separate from a generic UK classification. Studio names were cleaned to remove inconsistencies whilst preserving their essential identity. I created binary indicator fields for championships, podium finishes, and top-ten placements to facilitate analysis.

The final cleaned dataset contains 1,953 rows and 13 columns with complete data quality. Each record includes year, division, category, dance type, team size, co-ed status, rank, the derived indicator variables, studio name, team name, and country

### Data Visualisation
The Tableau dashboard provides multiple interactive views of the data. Key performance indicators show total championships, countries represented, years covered, and total performances at a glance.  The main visualisation tracks championship over time through an area chart, revealing growth patterns from 2015 to 2025. Additional charts show top countries by championship wins, a geographic world map displaying global distribution, dance style breakdown, and a detailed table of top-performing studios. 

### Challenges and Solutions 
The web scraping phase required handling varying HTML structures across different years, which I addressed through flexible parsing functions. Missing or incomplete data necessitated careful decisions about record inclusion versus exclusion, prioritising data quality over completeness. Data cleaning challenges included standardising country names whilst maintaining meaningful regional distinctions and cleaning studio names without losing their identity. The visualisation phase required balancing comprehensive data representation with clarity, achieved through strategic filtering and interactive elements that allow users to explore details on demand.

### Data Source
Primary data source is The Dance Worlds official competition results from thedanceworlds.com, covering 2015-2025 competition seasons. Last updated October 2025.
