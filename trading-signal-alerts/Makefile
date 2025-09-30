# RapidShip Universal Commands for Trading Signal Alerts
.PHONY: dev test build ship preview logs rollback doctor

# Development
dev:
	@./scripts/dev.sh

test:
	@./scripts/test.sh

lint:
	@./scripts/lint.sh

# Building
build:
	@./scripts/build.sh

preview:
	@./scripts/preview.sh

# Deployment
ship:
	@./scripts/ship.sh $(ENV)

rollback:
	@./scripts/rollback.sh $(VERSION)

# Operations
logs:
	@./scripts/logs.sh $(ENV) $(TAIL)

metrics:
	@./scripts/metrics.sh

doctor:
	@./scripts/doctor.sh

# Database
db-migrate:
	@./scripts/db-migrate.sh $(ENV)

db-seed:
	@./scripts/db-seed.sh $(ENV)

db-reset:
	@./scripts/db-reset.sh $(ENV)

# Mobile app
mobile-build:
	@cd mobile && ./gradlew assembleDebug

mobile-install:
	@cd mobile && ./gradlew installDebug

mobile-release:
	@cd mobile && ./gradlew assembleRelease

# Trading-specific commands
signals-test:
	@python -m pytest tests/test_signals.py -v

oanda-check:
	@python scripts/check_oanda_connection.py

fcm-test:
	@python scripts/test_fcm_notification.py

# Utilities
clean:
	@./scripts/clean.sh

update:
	@./scripts/update.sh

help:
	@echo "Trading Signal Alerts Commands:"
	@echo "  make dev              - Start signal backend server"
	@echo "  make test             - Run test suite"
	@echo "  make ship             - Deploy to production"
	@echo "  make preview          - Get shareable preview URL"
	@echo "  make logs             - Tail production logs"
	@echo "  make mobile-build     - Build Android APK"
	@echo "  make signals-test     - Test signal generation logic"
	@echo "  make oanda-check      - Verify OANDA API connection"
	@echo "  make fcm-test         - Test Firebase push notifications"
	@echo "  make doctor           - Diagnose issues"
