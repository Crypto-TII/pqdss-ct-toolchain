pipeline {
    agent none

    stages {
        stage('Matrix build') {
            matrix {
                agent any
              
                axes {
                    axis {
                        name 'TARGET'
                        values 'mac_os_x', 'mac_os_x_64', 'arm64', 'x86_64', 'mingw_x64', 'mingw_x64_AVX2'
                    }
                    
                    axis {
                        name 'MAU'
                        values 'True', 'False'
                    }
                }

                stages {
                    stage('Execute API tests') {
                        steps {
                            echo "$TARGET - $MAU"
                        }
                    }
                }
            }
        }
        
        stage('Build mingw_x64 - True') {
            steps {
                echo 'mingw_x64 - True'
            }
        }
        
        stage('Build mingw_x64 - False') {
            steps {
                echo 'mingw_x64 - False'
            }
        }
        
        stage('Build mingw_x64_AVX2 - True') {
            steps {
                echo 'mingw_x64_AVX2 - True'
            }
        }
        
        stage('Build mingw_x64_AVX2 - False') {
            steps {
                echo 'mingw_x64_AVX2 - False'
            }
        }
    }
}

