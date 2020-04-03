# Build from Latest Jenkins Image
FROM jenkins/jenkins:latest

# Install plugins required, if you have an environment with the plugins installed, you can use command to get the names:
# ls -l $JENKINS_HOMD/plugins

RUN /usr/local/bin/install-plugins.sh git matrix-auth workflow-aggregator docker-workflow blueocean credentials-binding sonar performance

# Change the default user name and password, comment out 2 lines below if you want set up yourself.
ENV JENKINS_USER sysadmin
ENV JENKINS_PASS think4me

# Skip initial setup
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false

# Copy executors.groovy and default-user.groovy scripts to run at first startup
COPY executors.groovy /usr/share/jenkins/ref/init.groovy.d/
COPY default-user.groovy /usr/share/jenkins/ref/init.groovy.d/

# Configure Jenkins Home folder
VOLUME /var/jenkins
