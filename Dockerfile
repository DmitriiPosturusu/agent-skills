# Dockerfile
# Java 17 + Maven multi-stage build
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /workspace

# Copy only build descriptors first for dependency caching
COPY pom.xml ./
COPY .mvn .mvn
COPY mvnw ./
RUN mvn -B -DskipTests dependency:go-offline || true

# Copy sources and build
COPY src ./src
RUN mvn -B -DskipTests package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /workspace/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
