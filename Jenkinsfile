pipeline {
    agent any
    stages {
        stage('Install') {
            steps {
                sh 'pip3 install -r requirements.txt --break-system-packages'
            }
        }
        stage('Lint') {
            steps {
                sh 'pip3 install flake8 --break-system-packages'
                sh 'python3 -m flake8 . --max-line-length=120 --exclude=.git --ignore=E501,W,C,E'
            }
        }
    }
    post {
        always {
            emailext(
                to: "alirezarogni@gmail.com",
                subject: "Build ${currentBuild.currentResult}: ${JOB_NAME}",
                body: "Build ${BUILD_NUMBER} - ${currentBuild.currentResult}\nCheck: ${BUILD_URL}"
            )
        }
    }
}
