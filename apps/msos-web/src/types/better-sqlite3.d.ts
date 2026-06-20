declare module "better-sqlite3" {
  interface Statement {
    get(...params: unknown[]): unknown;
    all(...params: unknown[]): unknown[];
    run(...params: unknown[]): unknown;
  }

  interface DatabaseInstance {
    prepare(source: string): Statement;
    exec(source: string): this;
    close(): void;
  }

  namespace Database {
    type Database = DatabaseInstance;
  }

  interface DatabaseConstructor {
    new (filename: string, options?: Record<string, unknown>): Database.Database;
  }

  const Database: DatabaseConstructor;
  export = Database;
}
