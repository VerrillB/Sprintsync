pipeline {
    agent any
    triggers { pollSCM('* * * * *') }
    environment {
        WEBEX_BOT_TOKEN = credentials('webex-bot-token')
        WEBEX_ROOM_ID   = credentials('webex-room-id')
    }
    stages {
        stage('Install') {
            steps { sh 'python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt' }
        }
        stage('Lint') {
            steps { sh '. venv/bin/activate && flake8 sprintsync tests' }
        }
        stage('Unit Test') {
            steps { sh '. venv/bin/activate && pytest --junitxml=results.xml' }
        }
    }
    post {
        always  { junit 'results.xml' }
        success { sh '. venv/bin/activate && python -m sprintsync.notify --status SUCCESS' }
        failure { sh '. venv/bin/activate && python -m sprintsync.notify --status FAILURE' }
    }
}
