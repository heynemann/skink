Feature: Add project
    As a software developer
    I want to add a project to Skink
    So that I can develop better softwares

    Scenario: Add a project with right data
        Given I am logged in
        And I go to new project page
        When I submit the form with the following data:
            | name               | git_repository                                    | build_script | branch  | monitor |
            | splinter           | git://github.com/cobrateam/splinter.git           | make tests   | master  | True    |
            | lettuce            | git://github.com/gabrielfalcao/lettuce.git        | make tests   | master  | True    |
            | flask-mongoalchemy | git://github.com/cobrateam/flask-mongoalchemy.git | make build   | release | False   |
        Then I should be redirected to the projects list page
        And it should contains the projects saved above
