# Maayan Dashboard

A data collection and visualization tool for marketing metrics. This tool collects data from Facebook Ads and Luma, calculates key marketing metrics, and displays them on a Geckoboard dashboard.

## Features

- Facebook Ads data collection
- Luma events data collection
- Marketing metrics calculation
- Customer Lifetime Value (LTV) tracking
- Daily revenue and guest tracking
- Automated data collection and dashboard updates

## Requirements

- Python 3.10+
- Virtual environment
- Facebook Ads API access
- Luma API access
- Geckoboard API access

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd maayandashboard
```

2. Run the installation script:
```bash
./scripts/install.sh
```

3. Configure your environment variables in `.env`:
```bash
vim .env
```

Required environment variables:
- `FACEBOOK_ADS_TOKEN`: Facebook Ads API token
- `LUMA_API_KEY`: Luma API key
- `GECKOBOARD_API_KEY`: Geckoboard API key

## Usage

### Manual Run

To run the data collection pipeline manually:
```bash
./scripts/run.sh
```

### Automated Collection

The installation script sets up a cron job to run the pipeline every 6 hours. You can check the cron logs in `logs/cron.log`.

To modify the schedule, edit your crontab:
```bash
crontab -e
```

## Directory Structure

```
maayandashboard/
├── src/                    # Source code
│   ├── collectors/        # Data collectors
│   ├── calculator/        # Metrics calculation
│   └── utils/            # Utilities
├── scripts/               # Deployment scripts
├── logs/                  # Log files
└── tests/                # Test files
```

## Monitoring

- Check the logs directory for detailed logs
- The pipeline logs all metrics and errors
- Failed runs will be logged with error details

## Troubleshooting

1. Check the logs in `logs/` directory
2. Ensure all API keys are valid
3. Verify network connectivity to APIs
4. Check Python environment is activated

## Development

To set up a development environment:

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[License information] 