test:
	docker-compose run app sh -c "python manage.py test"

lint:
	docker-compose run app sh -c "flake8"

migrations:
	docker-compose run app sh -c "python manage.py makemigrations"

migrate:
	docker-compose run app sh -c "python manage.py migrate"