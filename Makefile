.PHONY: build test clean example


build:
	python3.5 setup.py sdist

bundle:
	# bundle all what need to run this code (in case you board doesn't bundle all micropython-lib)
	docker run --rm -v ${PWD}:/scripts mrooding/micropython-docker -m upip install -r /scripts/requirements.txt -p /scripts/bundle
	# change premission so it can be delete by non root users
	docker run --rm -v ${PWD}:/scripts --entrypoint '/bin/bash'  mrooding/micropython-docker -c 'chmod -R 777 /scripts/bundle'

test: bundle
	docker run --rm -e MICROPYPATH=/scripts -v ${PWD}/bundle:/scripts/ -v ${PWD}/buzzer:/scripts/buzzer -v ${PWD}/test:/scripts/test mrooding/micropython-docker  /scripts/test/test_buzzer.py
	docker run --rm -e MICROPYPATH=/scripts -v ${PWD}/bundle:/scripts/ -v ${PWD}/buzzer:/scripts/buzzer -v ${PWD}/test:/scripts/test mrooding/micropython-docker  /scripts/test/test_midi.py

example: bundle
	docker run --rm -e MICROPYPATH=/scripts -v ${PWD}/bundle:/scripts/ -v ${PWD}/buzzer:/scripts/buzzer -v ${PWD}/example:/scripts/example mrooding/micropython-docker /scripts/example/example.py
	
clean:
	rm -rf build/ *.egg-info/ dist/ __pycache__/ bundle/

