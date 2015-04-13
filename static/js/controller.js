'use strict';

function MainController($scope, $http) {
    $scope.parentobj = {};
    $scope.parentobj.links = []
    $scope.hide = true
    $scope.display = ""
    $scope.loading = false
    $scope.images = false
    $scope.label = ""
    $scope.job_list = []
    $scope.catgry_all_imgs = {}
    $scope.hide_category = false
    $scope.added_category = false
    $scope.jobID = " ( No job started / selected )"

    if(document.cookie.indexOf("user") < 0) {
        $scope.hide = true
        window.location = "/login"
    }
    else {
        $scope.hide = false
    }

    function deleteAllCookies() {
        var cookies = document.cookie.split(";");

        for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i];
          var eqPos = cookie.indexOf("=");
          var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
          document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
        }
    }

    $scope.list_jobs = function(){
        var params = {};
        var result = $http({
            url: '/listjob',
            method: "POST",
            data: params,
            headers: {'Content-Type': 'application/json'}
            }).
            success(function(data) {
                $scope.job_list = data['list']
            }).
            error(function(data,status) {
            });
    }

    $scope.setjob = function(job_id){
        var params = {'job_id':job_id};
        var result = $http({
            url: '/setjob',
            method: "POST",
            data: params,
            headers: {'Content-Type': 'application/json'}
            }).
            success(function(data) {
                $scope.jobID = job_id
            }).
            error(function(data,status) {
            });
    }

    $scope.viewcat = function(){
        var params = {};
        var result = $http({
            url: '/viewcat',
            method: "POST",
            data: params,
            headers: {'Content-Type': 'application/json'}
            }).
            success(function(data) {
                $scope.added_category = true
                $scope.hide_category = false
                $scope.catgry_all_imgs = data
            }).
            error(function(data,status) {
            });
    }

    $scope.logout = function(){
        deleteAllCookies()
        window.location = "/login"
    }

    $scope.file = function(){
        $scope.hide_category = true
        $scope.added_category = false
        $scope.loading = true
        $scope.parentobj.links = []
        $scope.display = ""
        $scope.label = ""
        console.log("File");

        var params = {"search":$scope.search};
        var result = $http({
            url: '/file',
            method: "POST",
            data: params,
            headers: {'Content-Type': 'application/json'}
            }).
            success(function(data) {
                $scope.jobID = data['job_id']
                data = data['links']
                $scope.images = true
                for (var i in data['links']) {
                    $scope.parentobj.links.push(data['links'][i]['thumblink'])
                }
                $scope.loading = false
                $scope.display = "Showing thumbnails of images added with label as :" 
                $scope.label = $scope.search
            }).
            error(function(data,status) {
            });
        }
}