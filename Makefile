.PHONY: build test clean example


DOCKER_IMAGE=mitchins/micropython-linux
DOCKER_TEST_CMD=docker run --rm -e MICROPYPATH=/scripts -v ${PWD}/bundle:/scripts/ -v ${PWD}/buzzer:/scripts/buzzer -v ${PWD}/test:/scripts/test ${DOCKER_IMAGE}

build:
	python3 setup.py sdist

bundle:
	# bundle all what need to run this code (in case you board doesn't bundle all micropython-lib)
	docker run --rm -v ${PWD}:/scripts ${DOCKER_IMAGE} micropython -m upip install -r /scripts/requirements.txt -p /scripts/bundle
	# change premission so it can be delete by non root users
	docker run --rm -v ${PWD}:/scripts --entrypoint '/bin/bash' ${DOCKER_IMAGE} -c 'chmod -R 777 /scripts/bundle'

test: bundle
	${DOCKER_TEST_CMD} micropython /scripts/test/test_buzzer.py
	${DOCKER_TEST_CMD} micropython /scripts/test/test_midi.py

example: bundle
	docker run --rm -e MICROPYPATH=/scripts -v ${PWD}/bundle:/scripts/ -v ${PWD}/buzzer:/scripts/buzzer -v ${PWD}/example:/scripts/example ${DOCKER_IMAGE} micropython /scripts/example/example.py
	
clean:
	rm -rf build/ *.egg-info/ dist/ __pycache__/ bundle/

