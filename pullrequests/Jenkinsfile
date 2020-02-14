pipeline {
    agent any
    parameters {
        string(defaultValue: 'master', description: 'Which branch?', name: 'BRANCH_FROM')
    }
    options {
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '3'))
        disableConcurrentBuilds()
    }

    triggers {
        GenericTrigger(
            genericVariables: [
                [key: 'BRANCH_FROM', value: '$.pullrequest.fromRef.branch.name', expressionType: 'JSONPath', regexpFilter: '^((?!(release|feature)).)*$']
            ],
            
            causeString: 'Triggered on Pull request $BRANCH_FROM',
            
            token: 'feature_csis3',
            
            printContributedVariables: true,
            printPostContent: true,
        )
    }    
    stages {
        stage('Checkout'){
            parallel {
                stage('Checkout-Internal') {
                    steps{
                        ws('/opt/devops/pullrequest/tomcat'){
                            echo "Workspace dir is ${pwd()}"
                            echo "Branch to be checked out is ${params.BRANCH_FROM}"
                            checkout([$class: 'GitSCM', branches: [[name: BRANCH_FROM]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'PruneStaleBranch'], [$class: 'RelativeTargetDirectory', relativeTargetDir: 'apache']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'Jenkins', url: 'https://github.com/apache/tomcat.git']]])
                        }
                        notifyBitbucketServer('INPROGRESS') 
                    }
                }
                //stage('Checkout-External') {
                //    steps{
                //        ws('/opt/devops/pullrequest/project2'){
                //            echo "Workspace dir is ${pwd()}"
                //            echo "Branch to be checked out is ${params.BRANCH_FROM}"
                //            checkout([$class: 'GitSCM', branches: [[name: BRANCH_FROM]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'PruneStaleBranch'], [$class: 'RelativeTargetDirectory', relativeTargetDir: 'apache']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'Jenkins', url: 'https://github.com/apache/tomcat.git']]])
                //        }
                //        notifyBitbucketServer('INPROGRESS') 
                //    }
                }
            }
        }

        stage('Build'){
            parallel {
                stage('Build-Internal'){
                    steps{
                        sh '/opt/devops/buildscripts/tomcat/buildTomcatExample.sh'
                        echo 'Tomcat Example Build Done!'
                    }
                }
                //stage('Build-External'){
                //    steps{
                //        sh '/opt/auto_build/csis3_external/pullrequest/workspace/buildApplication.sh'
                //        echo 'Hello I am done'
                //    }
                }                
            }
        }
    }
    post {
        success {
            echo " Build Success"
            emailext (
                subject: "SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: '${SCRIPT, template="jenkins-matrix-email-html.template"}',
                recipientProviders: [[$class: 'CulpritsRecipientProvider'],[$class: 'RequesterRecipientProvider'], [$class: 'DevelopersRecipientProvider']],
                to:'feijiangnan@hotmail.com ou.yuan@gmail.com',
                mimeType: 'text/html'
            )
            notifyBitbucketServer('SUCCESS') 
        }
        failure {
            echo " Build Failed"
            emailext (
                subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: '${SCRIPT, template="jenkins-matrix-email-html.template"}' ,
                recipientProviders: [[$class: 'CulpritsRecipientProvider'],[$class: 'RequesterRecipientProvider'], [$class: 'DevelopersRecipientProvider']],
                to:'feijiangnan@hotmail.com ou.yuan@gmail.com',
                attachLog: true, 
                compressLog:false,
                mimeType: 'text/html'
            )
            notifyBitbucketServer('FAILED') 
        }
    }    
}

def notifyBitbucketServer(def state) {
    if('SUCCESS' == state || 'FAILED' == state) {
        currentBuild.result = state         // Set result of currentBuild !Important!
    }
    //notifyBitbucket commitSha1: '', considerUnstableAsSuccess: false, credentialsId: 'Jenkins',    disableInprogressNotification: false, ignoreUnverifiedSSLPeer: true, includeBuildNumberInKey: false, prependParentProjectKey: false, projectKey: '', stashServerBaseUrl: 'https://logstash.goweekend.ca'
}
