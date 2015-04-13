'use strict';

angular.module('Cloudcv-vatsal', ['ngRoute','ui.bootstrap'])
	.config(['$routeProvider', '$locationProvider',
		function($routeProvider, $locationProvider) {
		$routeProvider
		.when('/', {
			templateUrl: 'static/index.html',
			controller: MainController,
			resolve: MainController.resolve
		})
		.otherwise({
			redirectTo: '/'
		})
		;

		$locationProvider.html5Mode(false);
	}])
;
