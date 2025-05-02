# TLD Query Generator

This project generates Microsoft Defender queries based on TLD (Top-Level Domain) data from the SANS Internet Storm Center / DShield API.

## Legal Notice

### Data Source Attribution
This project uses data from the SANS Internet Storm Center / DShield API, which is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

### Usage Terms
- This project is for educational, research, and network protection purposes
- The generated queries are not guaranteed to be accurate or complete
- The API is provided "as-is" on a "best-effort" basis
- Do not build mission-critical applications around this data
- Do not resell or commercially redistribute the data
- Always validate queries in your own environment before deployment
- In case of API rate limiting (429 responses), respect the "Retry-After" header

### Commercial Use
While the data is licensed under CC BY-NC-SA 4.0, the API terms explicitly allow:
- Using the data for commercial purposes to protect your own company's network
- Building security tools and queries for internal use
- Implementing network protection measures based on the data

### Disclaimer
This project is not affiliated with or endorsed by SANS Institute or the Internet Storm Center. The generated queries are provided "as-is" without any warranty of any kind, either expressed or implied.

## User-Agent Information
This project uses a custom User-Agent for API requests:
```
TLDQueryGenerator/1.0 (GitHub: Robinzor)
```

## License
This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) License](https://creativecommons.org/licenses/by-nc-sa/4.0/) - see the [LICENSE](LICENSE) file for details. 